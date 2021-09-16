# FinalProject_Derco
Final Project
In this project I have decided to analyse four major Czech betting offices in terms of the rates they offer to their clients.
For this analysis I will scrape live data from the urls of these betting office of two sports - voleyball and tenis - as these two sports usually offer bets on only win or loss scenarios (**home** and **away** terms are being used in betting terminology) which simplyfies the analysis and calculations. Other observations (such as betting on total winner of a tournament etc.) will be dropped out of the dataset used for analysis.
Using a simple formula

**exchangeProfit = 1/homerate + 1/awayrate**

we can evaluate which of these four betting offices provides its clients with the "best and worst" rates in terms of securing its own profits. 
Statistically, the total sum of probabilities of all possible outcomes sums up to 1.
In the world of betting offices this formula will rather equal > 1 as their aim is to secure their profits with providing "unfair" rates, ie. summing up the reciprocal values of the "home" and "away" rates will be > 1, the higher the number, the more unfair the rates are.

First part of the code, **Scraper**, is being ran through command line 'python Scraper.py *argument*' with valid arguments *tenis*, *voleyball* or *all*

# Processor
In this part we will match and clean our data scraped from 4 different webpages.
We try to match same matches (games/sport events, for clarity) as each of the webpages names them slightly differently. 
First, we find the betting office with the highest amount of available matches. Then, we find unique dates and playtimes. Next, we try to match the matches by playtime across our 4 different datasets. Now, we try to ensure we matched the identical matches by looking for matches starting with the same 1st word among the ones with the same playtime. If we get 1 exact match, we are happy. We save these matches into a dataset.
As I mentioned before, even with our selection of sports, there still may be some "special" bets placed on the total winner of a tournament etc., providing only one rate.
We will get rid of these observations applying our formula, as these bets will fail to pass the following condition 
**1/homerate + 1/awayrate > 1**
Also, we get rid of all other unnecessary observations that could disrupt our further analysis and we save the ratios of all the individual matches for all individual betting offices and also their total averages. 

# Results
1st we plot the total averages of individual betting offices and evaluate the results. From the simple barchart we can see, that the average best rates (the most fair) offered for the actual data are by Fortuna, while SynotTip offers their clients with the worst ones. As Chance is being owned by the Tipsport holding, it is rather logical it provides their clients with the same rates as Tipsport. 

Looking at the boxplot charts of individual booking offices using our full data on rates (excluding error ones) gives us slightly more specific overview of the situation. We can see that according to median values, even SynotTip provides its clients with similar rates like Tipsport and Chance with several outliers drawing the average value upwards, while Fortuna remains a clear winner in terms of offered rates.

Even though we can make certain assumptions using this analysis, it would be more convenient to store daily data over a longer time span or include more sports (or ideally both) to enrich the dataset as our most actual dataset for 05/09/2021 contains around 150 observations.
