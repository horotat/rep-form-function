library(dplyr)
library(ggplot2)

dep <- read.csv("../data/depparse_coco_val.csv", header=TRUE)
omi <- read.csv("../data/omission_coco_val.csv", header=TRUE)

omi_v <- omi %>% select(-omission_t) %>% rename(score=omission_v) %>% mutate(pathway="visual")
omi_t <- omi %>% select(-omission_v) %>% rename(score=omission_t) %>% mutate(pathway="textual")

data_v <- merge(dep, omi_v) 
data_t <- merge(dep, omi_t) 
dep_lev <- (data_v %>% group_by(dep) %>% summarize(median_score=median(score)) %>% 
              data.frame %>% arrange(median_score))$dep 
postag_lev <- (data_v %>% group_by(postag) %>% summarize(median_score=median(score)) %>%
              data.frame %>% arrange(median_score))$postag

data <- rbind(data_t, data_v) %>% 
  mutate(dep = factor(dep, levels=dep_lev), 
         postag = factor(postag, levels=postag_lev))

filter_by_count <- function(dat, col, count) {
  dat[dat[,col] %in% names(table(dat[,col]))[table(dat[,col]) > count],]
}
MINCOUNT<-500


# FIGURE 2
ggplot(filter_by_count(data, "postag", MINCOUNT)) +
  aes(x=postag, y=score, color=pathway) +
  geom_boxplot(outlier.colour = 'grey', outlier.size = 1, varwidth = FALSE) +
  coord_flip() +
  theme(text=element_text(size=15)) +
  xlab("Part of Speech") +
  ggsave(file="../doc/imaginet-omission-pos-boxplot.png",
         width=5, height=5)
   

ggplot(filter_by_count(data, "dep", MINCOUNT)) +
       aes(x=dep, y=score, color=pathway) +
  geom_boxplot(outlier.colour = 'grey', outlier.size = 1, varwidth = FALSE) +
  coord_flip() +
  theme(text=element_text(size=15)) +
  xlab("Dependency") +
  ggsave(file="../doc/imaginet-omission-dep-boxplot.png",
         width=5, height=5)


# FIGURE 3
ratio <- filter(data, pathway=='visual')$score / filter(data, pathway=='textual')$score
data_r <- filter(data, pathway=="visual") %>% mutate(ratio=ratio, 
                                                    postag=reorder(postag, ratio, median),
                                                    dep=reorder(dep, ratio, median))
ggplot(filter_by_count(data_r,"postag",MINCOUNT) %>% filter,
       aes(x=postag, y=log(ratio))) +
  geom_boxplot(outlier.colour = 'grey', outlier.size = 1, varwidth = FALSE) +
  coord_flip() +
  theme(text=element_text(size=15)) +
  xlab("Part of Speech")
ggsave(file="../doc/imaginet-omission-ratio-pos-boxplot.png", width=5, height=5)

ggplot(filter_by_count(data_r,"dep",MINCOUNT) %>% filter,
       aes(x=dep, y=log(ratio))) +
  geom_boxplot(outlier.colour = 'grey', outlier.size = 1, varwidth = FALSE) +
  coord_flip() +
  theme(text=element_text(size=15)) +
  xlab("Dependency")
ggsave(file="../doc/imaginet-omission-ratio-dep-boxplot.png", width=5, height=5)