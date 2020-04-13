
library(tidyverse)

returns <- read_csv("returns_for_analysis.csv")

capm_mom <- lm(Momentum~Market, data=returns)
summary(capm_mom) # Slope Coefficient: -0.153138 (SI: t-value -0.766)

capm_vtv <- lm(VTV~Market, data=returns)
summary(capm_vtv) # Slope Coefficient: 0.9759733 (SS: t-value 43.277)

capm_spy <- lm(SPY~Market, data=returns)
summary(capm_spy) # Slope Coefficent: 1.0009569 (SS: t-value 423.55)

#######################################################################################

returns_daily <- read_csv("ETF_Analysis/MOM_SPY_VTV_MKT_returns.csv")

capm_mom <- lm(Momentum~MKT, data=returns_daily)
summary(capm_mom) # Slope Coefficient: -0.0170553 (SI: t-value -0.515)

capm_vtv <- lm(VTV~MKT, data=returns_daily)
summary(capm_vtv) # Slope Coefficient: 0.9681 (SS: t-value 257.966)

capm_spy <- lm(SPY~MKT, data=returns_daily)
summary(capm_spy) # Slope Coefficient: 0.9938 (SS: t-value 947.319)

ggplot(data=returns_daily, aes(x=X1, y=Momentum))+
  geom_point()





