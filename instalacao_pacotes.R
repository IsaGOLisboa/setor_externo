##################################################################################
#                 INSTALAÇÃO E CARREGAMENTO DE PACOTES NECESSÁRIOS               #
##################################################################################
#Pacotes utilizados
pacotes <- c("dplyr","tidyr","purrr","magrittr", 'ggplot2', 'reshape2',
             "plotly", "stats", "car", "ggrepel", "kaleido", "webshot", 
             "reticulate", "processx", "magick")

options(rgl.debug = TRUE)

if(sum(as.numeric(!pacotes %in% installed.packages())) != 0){
  instalador <- pacotes[!pacotes %in% installed.packages()]
  for(i in 1:length(instalador)) {
    install.packages(instalador, dependencies = T)
    break()}
  sapply(pacotes, require, character = T) 
} else {
  sapply(pacotes, require, character = T) 
}

####Inicializando o script no venv para utilizar a interface com Python para utilização do keleido
reticulate::py_last_error()
reticulate::use_virtualenv("C:/Users/User/Desktop/papel_celulose/papel_celulose", required = TRUE)
reticulate::py_config()
reticulate::import("kaleido")
reticulate::py_install(c("plotly", "kaleido"))
