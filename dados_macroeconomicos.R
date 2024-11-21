install.packages(c('dplyr','tidyr',"purrr","magrittr"))
library(dplyr)
library(tidyr)
library(purrr)
library(magrittr)

version

# Séries e códigos disponíveis ipea
series_ipeadata <- ipeadatar::available_series()
series_ipeadata
# Filtrar séries com o termo "caged"
dplyr::filter(
  series_ipeadata,
  stringr::str_detect(source, stringr::regex("caged", ignore_case = TRUE))
)

##############Obtenção das séries####################
#PAN12_IPCAG12 - IPCA mensal (taxa total de variação (%a.a))
IPCA<- ipeadatar::ipeadata("PAN12_IPCAG12",language=c("en","br"),quiet=FALSE)
IPCA<- IPCA%>%
  filter(date >= as.Date("2014-08-01"))%>%
  select(2,3)%>%
  rename(Data = date,
         IPCA = value)%>%
  mutate(Data = format(Data,"%m/%Y"))
  
  
  
#PAN4_PIBPMG4 -  PIB real trimestral 
PIB_trimestral <- ipeadatar::ipeadata("PAN4_PIBPMG4",language=c("en","br"),quiet=FALSE)
PIB_trimestral<- PIB_trimestral%>%
  filter(date >= as.Date("2014-06-01"))%>%
  select(2,3)%>%
  rename(Data = date,
         PIB = value)%>%
  mutate(data = format(Data,"%m/%Y"))

datas_mensais <- data.frame(
  Data = seq(as.Date("2014-07-01"), as.Date("2024-08-01"), by = "month")
)
PIB_trimestral$Data <- as.Date(PIB_trimestral$Data)
PIB_trimestral<- left_join(datas_mensais, PIB_trimestral, by = "Data")
PIB_trimestral<-PIB_trimestral%>%
  fill(PIB, .direction = "down")%>%
  select(1,2)%>%
  slice(-1)%>%
  mutate(data = format(Data,"%m/%Y"))%>%
  select(2,3)%>%
  rename(Data = data)

#PAN12_TJOVER12 - Taxa de Juros - SELIC -over mensal
SELIC_mes<-ipeadatar::ipeadata("PAN12_TJOVER12",language=c("en","br"),quiet=FALSE)
SELIC_mes<- SELIC_mes%>%
  filter(date >= as.Date("2014-08-01"))%>%
  select(2,3)%>%
  rename(Data = date,
         SELIC_mes = value)%>%
  mutate(Data = format(Data,"%m/%Y"))

#BM366_TJOVER366 - Taxa de juros - SELIC - fixada pelo Copom (%a.a)
SELIC_copom<- ipeadatar::ipeadata("BM366_TJOVER366",language=c("en","br"),quiet=FALSE)
SELIC_copom<-SELIC_copom%>%
  filter(date>= as.Date("2014-08-01"))%>%
  select(2,3)%>%
  rename(Data = date,
         SELIC_copom = value)%>%
  mutate(Data = format(Data,"%m/%Y"))
  




SELIC<- left_join(SELIC_mes, SELIC_copom, by = "Data")



#Cambio
dados_sgs_dolar <- GetBCBData::gbcbd_get_series(
  id = c("Dólar" = 3698, "IBC-Br" = 24363, "Resultado Primário" = 5793),
  first.date = "2014-08-01",
  last.date = "2024-09-01",
  format.data = "wide"
)


cambio<- dados_sgs_dolar
cambio<- cambio%>%
  subset(select = -c(3:4))

cambio$Dólar <- as.numeric(as.character(cambio$Dólar))
cambio<- cambio%>%
  rename(Dolar = Dólar,
         Data = ref.date)%>%
  group_by(Data = format(as.Date(Data), "%m/%Y")) %>%   
  summarise(Dolar = mean(Dolar, na.rm = TRUE))%>%
  arrange()



#Importações: 	BPAG12_BCM12
importacoes<- ipeadatar::ipeadata("BPAG12_BCM12",language=c("en","br"),quiet=FALSE)
                                  
importacoes<- importacoes%>%
  filter(date >= as.Date("2014-08-01"))%>%
  select(2,3)%>%
  rename(Data = date,
         importacoes = value)%>%
  mutate(Data = format(Data,"%m/%Y"))

#Exportações: BPAG12_BCX12
exportacoes<- ipeadatar::ipeadata("BPAG12_BCX12",language=c("en","br"),quiet=FALSE)
exportacoes<- exportacoes%>%
  filter(date >= as.Date("2014-08-01"))%>%
  select(2,3)%>%
  rename(Data = date,
         exportacoes = value)%>%
  mutate(Data = format(Data,"%m/%Y"))

#Indice de confiança ao consumidor ICC: FCESP12_IIC12
icc<- ipeadatar::ipeadata("FCESP12_IIC12",language=c("en","br"),quiet=FALSE)
icc<- icc%>%
  filter(date >= as.Date("2014-08-01"))%>%
  select(2,3)%>%
  rename(Data = date,
         ICC = value)%>%
  mutate(Data = format(Data,"%m/%Y"))


 dados_macro <- IPCA %>%
  left_join(PIB_trimestral, by = "Data") %>%
  left_join(SELIC, by = "Data") %>%
  left_join(cambio, by = "Data") %>%
  left_join(importacoes, by = "Data") %>%
  left_join(exportacoes, by = "Data") %>%
  left_join(icc, by = "Data")

dados_macro<-dados_macro%>%
  distinct()


############################################################
write.csv(dados_macro, file= 'C:\\Users\\User\\Desktop\\mercado_exterior\\planilhas_verificadas\\dados_macro.csv', row.names = FALSE)

