# Knitr options
### Generic preamble
rm(list = ls(all.names = TRUE)) #will clear all objects includes hidden objects.
gc() #free up memrory and report the memory usage.
graphics.off()

Sys.setenv(LANG = "en") # For english language
options(scipen = 5) # To deactivate annoying scientific number notation

### Load packages
library(tidyverse) # Collection of all the good stuff like dplyr, ggplot2 ect.
library(magrittr) # For extra-piping operators (eg. %<>%)

# Descriptives
#library(skimr)
library(stargazer)
library(corrplot)
# ML
library(xgboost)
library(caret)  



setwd("G:/Github/ai_research")

df = read.csv("Data/seniority_dropout.csv")



data_dropout <- data %>%
  group_by(AID) %>%
  mutate(dropout = year == max(year, na.rm = TRUE)) %>%
  ungroup() %>%
  filter(year <= 2019) %>%
  mutate(seniority_bin = case_when(
    seniority <= 5 ~ "1 early",
    seniority > 5 & seniority <= 10 ~ "2 mid",
    seniority > 10 & seniority <= 15 ~ "3 mid late",
    seniority > 15 ~ "4 late",
  )
  )
