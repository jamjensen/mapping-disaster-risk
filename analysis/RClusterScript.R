library(pacman)
p_load(ggplot2)
p_load(dplyr)
p_load(tidyr)
p_load(factoextra)
p_load(readr)
p_load(clustertend)
p_load(psych)
p_load(fpc)
p_load(gridExtra)
p_load(seriation)
p_load(dendextend)
p_load(argparse)


#setwd("/home/jamesjensen")
print("TESTTTT")

parser <- ArgumentParser()
parser$add_argument('-i', '--input', action="store", dest='input', help='that csv')
parser$add_argument('-d', '--dir', action="store", dest='dir', help='home for all the output plots')
args <- parser$parse_args()


main_dir <- "/home/jamesjensen/scratch-midway2/zonal/"
sub_dir <- args$dir
output_dir <- file.path(main_dir, sub_dir)

if (!dir.exists(output_dir)){
  dir.create(output_dir)
} else {
  print("Dir already exists!")
}


print(args$input)
roof_matrix <- read_csv(args$input)
if (colnames(roof_matrix)[1] != "roof") {
  roof_matrix <- roof_matrix %>% rename(roof = X1)
}
roof_matrix <- roof_matrix[complete.cases(roof_matrix), ]
#print(head(roof_matrix))

#roof_matrix <- head(roof_matrix)
setwd(output_dir)

run_kmeans <- function(roof_matrix, clusters, filename) {
  ###This function runs the entire k-means algorithm ###
  
  # Scale and find covariance matrix
  roof_scaled <- roof_matrix %>% select(-roof) %>%
    scale()
  dist_can <- roof_scaled %>% dist(method="canberra")
  # Plot ODI
  title1 <- paste("ODI:", filename, sep=" ")
  viz <- fviz_dist(dist_can,
                   show_labels = FALSE,
                   gradient = list(low = "#00AFBB", mid = "white", high = "#FC4E07")) +
    ggtitle(title1)
  #plot(viz)
  ggsave(filename="viz.png", plot=viz)
  
  # K-means
  k2 <- kmeans(roof_scaled, centers=clusters, nstart = 15)
  output <- roof_matrix %>% select(roof)
  output$K_Cluster <- as.factor(k2$cluster)
  k_title <- paste("K = ", clusters, sep="")
  title2 <- paste(k_title, filename, sep=" ")
  group <- fviz_cluster(k2, geom = "point", data = roof_scaled) +
    ggtitle(title2)
  ggsave(filename = "group.png", plot=group)
  
  # Comparison to actual labels
  grouped <- aggregate(output,
                       by=list(output$roof, output$K_Cluster),
                       FUN=length)
  colnames(grouped)[colnames(grouped)=="Group.2"] <- "Cluster"
  actual_label_count <-table(roof_matrix$roof)
  title3 <- paste("Comparison to actual labels:", filename, sep=" ")
  bar <- ggplot(grouped, aes(fill=Cluster, y=K_Cluster, x=Group.1)) + 
    geom_bar(position="dodge", stat="identity") +
    xlab("Roof Material") +
    ylab("Count") +
    ggtitle(title3)
  ggsave(filename="kmeans_bar_xlab_roof.png", plot=bar)
  
  bar1 <- ggplot(grouped, aes(fill=Group.1, y=K_Cluster, x=Cluster)) + 
    geom_bar(position="dodge", stat="identity") +
    xlab("Cluster") +
    ylab("Count") +
    ggtitle("Group by Cluster")
  
  ggsave(filename="Kmeans_bar_xlab_cluster.png", plot=bar1)
  
  healthy <- c("concrete_cement", "healthy_metal")
  unhealthy <- c("irregular_metal", "other", "incomplete")
  output <- output %>% mutate(status = ifelse(roof %in% healthy, "healthy", "unhealthy"))
  output <- output %>% aggregate(by=list(output$status, output$K_Cluster), FUN=length) %>%
    select(Group.1, Group.2, roof) %>%
    rename('status' = 'Group.1', 'cluster' = 'Group.2', 'count' = 'roof')
  output <- output %>% group_by(cluster) %>% mutate(percent = (count/sum(count) * 100))
  
  write.csv(data.frame(output), file="kmeans_results.csv")
}


run_hac <- function(roof_matrix, clusters, distance, method, file) {
  ###This function runs the entire factor analysis algorithm ###
  
  # Scale
  roof_scaled <- roof_matrix %>% select(-roof) %>%
    scale() %>%
    dist(method=distance)
  hc_complete <- hclust(roof_scaled, method=method)
  title5 <- paste("HAC:", file, sep=" ")
  den <- plot(hc_complete %>%
         as.dendrogram %>%
         set("branches_k_color", k=clusters),
       leaflab="none",
       main = title5)
  ggsave(filename="dend.png",plot=den)
  
  # Cut the tree at k=5
  cut <- cutree(hc_complete, k=clusters)
  output <- roof_matrix %>% select(roof)
  output$K_Cluster <- as.factor(cut)
  grouped <- aggregate(output,
                       by=list(output$roof, output$K_Cluster),
                       FUN=length)
  colnames(grouped)[colnames(grouped)=="Group.2"] <- "Cluster"
  actual_label_count <-table(roof_matrix$roof)
  title3 <- paste("HAC Comparison to Actual Labels:", file, sep=" ")
  bar <- ggplot(grouped, aes(fill=Cluster, y=K_Cluster, x=Group.1)) + 
    geom_bar(position="dodge", stat="identity") +
    xlab("Roof Material") +
    ylab("Count") +
    ggtitle(title3)
  ggsave(filename="hac_bar.png", plot=bar)
  
  # Plot the inverse
  bar1 <- ggplot(grouped, aes(fill=Group.1, y=K_Cluster, x=Cluster)) + 
    geom_bar(position="dodge", stat="identity") +
    xlab("Cluster") +
    ylab("Count") +
    ggtitle("Group by Cluster")
  
  ggsave(filename= "hac_inverse.png", plot=bar1)
  
  
  healthy <- c("concrete_cement", "healthy_metal")
  unhealthy <- c("irregular_metal", "other", "incomplete")
  output <- output %>% mutate(status = ifelse(roof %in% healthy, "healthy", "unhealthy"))
  output <- output %>% aggregate(by=list(output$status, output$K_Cluster), FUN=length) %>%
    select(Group.1, Group.2, roof) %>%
    rename('status' = 'Group.1', 'cluster' = 'Group.2', 'count' = 'roof')
  output <- output %>% group_by(cluster) %>% mutate(percent = (count/sum(count) * 100))
  
  write.csv(data.frame(output), file="hac_results.csv")
}

run_PAM <- function(roof_matrix, clusters, name) {
  ## This function runs the entire PAM algorithm ##
  roof_scaled <- roof_matrix %>% 
    select(-roof) %>%
    scale()
  
  PAM <- pam(roof_scaled,
             k=clusters)
  output <- roof_matrix %>% select(roof)
  output$pamCluster <- as.factor(PAM$cluster)
  grouped <- aggregate(output,
                       by=list(output$roof, output$pamCluster),
                       FUN=length)
  
  pam_plt <-ggplot(grouped2, aes(fill=Group.1, y=pamCluster, x=Group.2)) + 
    geom_bar(position="dodge", stat="identity") +
    xlab("Roof Material") +
    ylab("Count") +
    ggtitle(name)
  ggsave(filename="pam_plt", plot=pam_plt)
  
  healthy <- c("concrete_cement", "healthy_metal")
  unhealthy <- c("irregular_metal", "other", "incomplete")
  output <- output %>% mutate(status = ifelse(roof %in% healthy, "healthy", "unhealthy"))
  output <- output %>% aggregate(by=list(output$status, output$K_Cluster), FUN=length) %>%
    select(Group.1, Group.2, roof) %>%
    rename('status' = 'Group.1', 'cluster' = 'Group.2', 'count' = 'roof')
  output <- output %>% group_by(cluster) %>% mutate(percent = (count/sum(count) * 100))
  
  write.csv(data.frame(output), file="pam_results.csv")
}

run_kmeans(roof_matrix, 2, "zonal_k2")
run_hac(roof_matrix, 2, distance="canberra", method="complete","zonal_hac2")
run_PAM(roof_matrix, 2, "zonal_pam2")


