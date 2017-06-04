library(data.table)
library(dplyr)
library(stringi)
library(mirt)
library(foreign)
dt = fread('extracted_data.csv')
dt[,success:= result_flag<=2]
dt= rename(dt, same_p_optimal = p_optimal)
dt[, p_dup:=duplicates/optstep]
dt[,f_m_ratio:= first_move_time/rest_mean]
dt[,fp_m_ratio:= first_push_time/rest_mean]
dt[,f_t_ratio:= first_move_time/guan_time]
dt[,fp_t_ratio:= first_push_time/guan_time]
dt[,p_higher:=num_higher_than_sd/steps]
dt[,maxbox := max(box_completed, na.rm = T), by = num]
dt[,comp_rate:= box_completed/maxbox]
dt[,dbox:=maxbox - box_completed]
dt[,c('maxbox', 'optstep'):=NULL]
dt[,time_window := quantile(guan_time, 0.4), by = num]
dt[, suc_within := success & guan_time<=time_window]
dt[,time_window:=NULL]
mean_var = c("box_completed","dsteps",
             "first_move_time","first_push_time",
             "guan_time","same_p_optimal","rest_mean","rest_sd",
             "p_dup","f_m_ratio","fp_m_ratio","f_t_ratio",
             "fp_t_ratio","p_higher","comp_rate","dbox")
sucdt = dt[success==T, lapply(.SD, mean, na.rm = T), by  = id,.SDcols = mean_var]
sucdt[,c("comp_rate",'dbox','box_completed'):=NULL]
lntrans = c("first_move_time","first_push_time","guan_time",
            "f_m_ratio","fp_m_ratio","f_t_ratio","fp_t_ratio")
for (var in lntrans){
  lnvar = 'ln' %s+% var
  sucdt[,(lnvar):=log(get(var))]
}

faildt = dt[success==F, lapply(.SD, mean, na.rm = T), by  = id,.SDcols = mean_var]
lntrans = c("first_move_time","first_push_time","guan_time",
            "f_m_ratio","fp_m_ratio","f_t_ratio","fp_t_ratio")
for (var in lntrans){
  lnvar = 'ln' %s+% var
  faildt[,(lnvar):=log(get(var))]
}
ndt = merge(sucdt, faildt, by = 'id', all.x = T, all.y = T)

ndt = dcast(dt, id~num, value.var = 'box_completed') %>% select(.,-id) %>%
  mirt(.,1,itemtype = 'gpcm') %>% fscores() %>% cbind(ndt,.) %>% rename(.,suc_theta = F1)
ndt = dt[,suc_within:=as.numeric(suc_within)] %>% dcast(., id~num, value.var = 'suc_within')  %>% 
  select(.,-id) %>% mirt(.,1,itemtype = 'Rasch', verbose = F) %>% 
   fscores %>% cbind(ndt,.) %>% rename(., suc_window = F1)

# I comment below codes because the variable generated below is highly correlated with suc_theta
#######################################################
# dt[,giveup:= as.numeric(result_flag==3)]
# 
# ndt = dcast(dt, id~num, value.var = 'giveup') %>% select(.,-id) %>% 
#   mirt(.,1,itemtype = 'Rasch', verbose = F) %>% fscores %>% cbind(ndt,.) %>%
#   rename(., giveup = F1)
#######################################################
yvar = read.spss('Grade 1+2-others-0313.sav', to.data.frame = T) %>% 
  select(., ID, contains('TM'), Raven) %>% data.table
yvar[,Rperc := rank(Raven)/sum(!is.na(Raven))]
yvar[Rperc>1,Rperc:= NA]
fares = select(yvar, contains('TM')) %>% fa
yvar = fares$scores %>% cbind(yvar,.)
yvar[,Mperc := rank(MR1)/sum(!is.na(MR1))]
yvar[Mperc>1,Mperc:= NA]
ndt = merge(yvar, ndt, by.x = "ID", by.y = "id", all.x = T, all.y = T)

Mpolar = ndt[Mperc>=0.75] %>% mutate(., Mperc=1)
Mpolar = ndt[Mperc<=0.25] %>% mutate(., Mperc=0) %>% rbind(.,Mpolar) %>%
  select(., -(ID:MR1))
Mpolar = Mpolar[complete.cases(Mpolar),] 
write.csv(Mpolar, 'Mpolar.csv')

Rpolar = ndt[Rperc>=0.75] %>% mutate(., Rperc=1)
Rpolar = ndt[Rperc<=0.26] %>% mutate(., Rperc=0) %>% rbind(.,Rpolar) %>%
  select(., -(ID:Raven), -(MR1:Mperc))
Rpolar = Rpolar[complete.cases(Rpolar),] 
write.csv(Rpolar, 'Rpolar.csv')
