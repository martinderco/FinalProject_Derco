import pandas as pd


def loadOffices(sport):
    """Loads .csv files with scraped data.

    :param sport: specific sport we load data for
    :return: loaded datasets for each observed betting office
    """
    chance = pd.read_csv('chance/' + sport + '.csv')
    ifortuna = pd.read_csv('ifortuna/' + sport + '.csv')
    synottip = pd.read_csv('synottip/' + sport + '.csv')
    tipsport = pd.read_csv('tipsport/' + sport + '.csv')

    chance = chance.sort_values(by=['date'])
    ifortuna = ifortuna.sort_values(by=['date'])
    synottip = synottip.sort_values(by=['date'])
    tipsport = tipsport.sort_values(by=['date'])

    return chance, ifortuna, synottip, tipsport


def findLargestByValue(chance, ifortuna, synottip, tipsport, value):
    """Finds betting office providing the most available matches.

    :param chance: betting office Chance
    :param ifortuna: betting office iFortuna
    :param synottip: betting office SynotTip
    :param tipsport: betting office Tipsport
    :param value: values 'name' or 'date' used as criteria to find office with the highest no. of matches available
    :return: betting office providing the highest number of unique matches
    """

    # setting max to -1 as we want to be sure this value will be overwritten by at least 0 matches at a specific playtime
    # we need to set "largest" value even if there are no matches for the code to work
    max = -1
    if (chance.size > max):
        largest = chance
        max = chance.size
    if (ifortuna.size > max):
        largest = ifortuna
        max = ifortuna.size
    if (synottip.size > max):
        largest = synottip
        max = synottip.size
    if (tipsport.size > max):
        largest = tipsport
    return largest[value].unique()

def computeFairnessRatio(row, identifier, office):
    """Calculates 'Fairness ratio' for individual matches.

    Here we apply our crucial formula to compute the 'Fairness ratio' or 'exchangeProfit' = 1/homerate + 1/awayrate
    This formula evaluates the exchange profit/margin of individual booking companies.
    Also, using 'identifier' this function checks whether we can find exactly one perfect match in order to append
    correct values.
    As we mentioned before, there still may be observations of bets, that do not bet on win-lose
    such are bets on final winner etc. therefore, we rule out these bets with a simple condition
    as these bets will have rates that fail to comply with our ratio (will be below 1).
    we save these ratios for each match for each company if available, otherwise append zero

    :param row: specific row where data on a match are stored
    :param identifier: first word in matches' name
    :param office: betting office
    """

    matches_for_date_dataset_select = office.loc[
        office['name'].str.contains(identifier)]
    # when we find exactly one match, we are happy, and save it as a list
    if (len(matches_for_date_dataset_select.index) == 1):
        values = matches_for_date_dataset_select.iloc[0].values.tolist()
        exchangeProfit = 1 / float(values[2]) + 1 / float(values[4])
        if (exchangeProfit > 1):
            row.append(exchangeProfit)
        else:
            row.append(0)
    else:
        row.append(0)

def analyze_exchange_profit_for_sport(sport):
    """Main Processor function.

    This function runs the whole analysing process - matching of individual games among betting offices
    by playtime and 'identifier' , calculating their 'Fairness ratio' and saving these values into final database
    used for future visualisation.

    :param sport: specific sport we want to analyse
    """
    rowsToAppend = []
    rowsToAppend.append(["Match_name", "Date", "Chance", "Ifortuna", "Synot", "Tipsport"])
    chance, ifortuna, synottip, tipsport = loadOffices(sport)

    dates = findLargestByValue(chance, ifortuna, synottip, tipsport, 'date')
    # create new dataframe for each playtime for each webpage
    for date in dates:
        matches_for_date_chance = chance.loc[chance['date'] == date]
        matches_for_date_ifortuna = ifortuna.loc[ifortuna['date'] == date]
        matches_for_date_synottip = synottip.loc[synottip['date'] == date]
        matches_for_date_tipsport = tipsport.loc[tipsport['date'] == date]
        # find the webpage with highest no. of observations for a specific playtime
        names = findLargestByValue(chance, ifortuna, synottip, tipsport, 'name')
        # second forloop to find the exact match by 1st word in the matches' name
        for name in names:
            try:
                # create blank array and add name and date
                row = []
                row.append(name)
                row.append(date)
                # here we try to clean the names of the matches of special symbols, that could complicate the matching process
                # parsed = divide name into single words and pick the 1st one
                parsed = str(name).replace(',', ' ').replace('/', ' ').split(' ')
                identifier = parsed[0]

                datasetsToEvaluate = [matches_for_date_chance, matches_for_date_ifortuna, matches_for_date_synottip, matches_for_date_tipsport]
                for office in datasetsToEvaluate:
                    computeFairnessRatio(row, identifier, office)

                # observations with incorrect/zero values shall not be appended
                if (row[2] == 0 and row[3] == 0 and row[4] == 0 and row[5] == 0):
                    continue
                else:
                    rowsToAppend.append(row)
            except:
                pass
    df = pd.DataFrame(rowsToAppend)
    df.to_csv(sport + '_final.csv', index=False, header=False)


analyze_exchange_profit_for_sport('tenis')
analyze_exchange_profit_for_sport('voleyball')