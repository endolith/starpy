import pandas as pd
from fractions import Fraction

def Allocated_Score(K, W, S):

    #Normalize score matrix
    ballots = pd.DataFrame(S.applymap(Fraction) / K, columns=S.columns)

    #Find number of voters and quota size
    V = ballots.shape[0]
    quota = Fraction(V, W)
    ballot_weight = pd.Series([Fraction(1)]*V,name='weights')

    #Populate winners in a loop
    winner_list = []
    while len(winner_list) < W:

        weighted_scores = ballots.multiply(ballot_weight, axis="index")

        #Select winner
        weighted_sums = weighted_scores.sum()
        #print(f'\nWeighted scores:\n{weighted_sums}')

        # Get the (candidate, score) pair with the maximum score.
        # If multiple candidates are tied, the first will be returned.
        w = max(weighted_sums.items(), key=lambda x: x[1])[0]
        #print(f'\nWinner: {w}')

        #Add winner to list
        winner_list.append(w)

        #remove winner from ballot
        ballots.drop(w, axis=1, inplace=True)

        #Create lists for manipulation
        cand_df = pd.concat([ballot_weight,weighted_scores[w]], axis=1).copy()
        cand_df_sort = cand_df.sort_values(by=[w], ascending=False).copy()

        #find the score where a quota is filled
        split_point = cand_df_sort[cand_df_sort['weights'].cumsum() < quota][w].min()

        #Amount of ballot for voters who voted more than the split point
        spent_above = cand_df[cand_df[w] > split_point]['weights'].sum()

        #Exhaust all ballots above split point
        if spent_above>0:
            cand_df.loc[cand_df[w] > split_point, 'weights'] = Fraction(0)

        #if split point = 0 then the winner did not get a full quota of support
        #otherwise there is a surplus

        #Amount of ballot for voters who gave a score on the split point
        weight_on_split = cand_df[cand_df[w] == split_point]['weights'].sum()

        if weight_on_split>0:
            #Fraction of ballot on split needed to be spent
            spent_value = (quota - spent_above)/weight_on_split

            #Take the spent value from the voters on the threshold evenly
            cand_df.loc[cand_df[w] == split_point, 'weights'] = cand_df.loc[cand_df[w] == split_point, 'weights'] * (1 - spent_value)

            #ballot_weight = cand_df['weights'].clip(0.0,1.0)
        ballot_weight = cand_df['weights']
    return winner_list
