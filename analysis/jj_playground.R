library(ggplot2)
library(dplyr)
library(tidyr)
library(factoextra)

setwd("/Users/jamesjensen/Documents/harris/q1_20/UML/Project/mapping-disaster-risk/data")

roof_matrix <- read_csv("300_roof_matrix.csv")

head(roof_matrix)

# remove all zeroes
# only necessary for matrices made without the zonal stats function
roof_matrix <- roof_matrix %>%
  select(-`3`) %>% 
  filter(!(`0`==0 & `1`==0 & `2`==0))

roof_scaled <- roof_matrix %>% 
  select( -roof) %>% 
  scale()

dist_man <- roof_scaled %>% 
  dist(method="manhattan")

dist_euc <- roof_scaled %>% 
  dist(method="euclidean")

dist_can <- roof_scaled %>% 
  dist(method="canberra")


plt_can <- fviz_dist(dist_can, show_labels = FALSE, gradient = list(low = "#00AFBB", 
                                                                    mid = "white", high = "#FC4E07")) + ggtitle("Euclidean")

plt_can

hs <- hopkins(roof_scaled, n=50)
hs <- round(as.numeric(as.character(unlist(hs))), digits=3)

k2 <- kmeans(roof_scaled, centers = 4, nstart = 15)

output <- roof_matrix %>% 
  dplyr::select(roof)

output$K_Cluster <- as.factor(k2$cluster)

p1 <- fviz_cluster(k2, geom = "point", data = roof_scaled) + ggtitle("k = 4")

p1
k2$centers

output

grouped <- aggregate(output, by=list(output$roof, output$K_Cluster),
                     FUN=length)
grouped

table(output$roof[output$K_Cluster == 1])
table(output$roof[output$K_Cluster == 2])

table(roof_matrix$roof)

ggplot(grouped, aes(fill=Group.2, y=K_Cluster, x=Group.1)) + 
  geom_bar(position="dodge", stat="identity")


PAM <- pam(roof_scaled,
           k=2)

output <- cbind(output, pamCluster = PAM$clustering)

PAM$clusinfo

roof_matrix %>% 
  filter(roof == 'incomplete')

head(roof_matrix)

