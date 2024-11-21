#Bibliotecas
library(ggplot2)
library(gganimate)
library(dplyr)



part_invest = read.csv("C:\\Users\\User\\Desktop\\mercado_exterior\\RELATORIO_DADOS_DE_MERCADO (B3) - dados_export.csv")

# Transformar os dados para o formato longo
part_invest_long <- part_invest %>%
  tidyr::pivot_longer(
    cols = -Ano,
    names_to = "Tipo_Investidor",
    values_to = "Porcentagem"
  )

part_invest_long

# Converter o campo Porcentagem em numérico 
part_invest_long$Porcentagem <- gsub("%", "", part_invest_long$Porcentagem)
part_invest_long$Porcentagem <- gsub(",", ".", part_invest_long$Porcentagem)

part_invest_long$Porcentagem<- as.numeric(part_invest_long$Porcentagem)
part_invest_long


###############Gráfico de barra horizontais
# Criando o diretório para salvar os frames
if (!dir.exists("part_invest_horizontal")) {
  dir.create("part_invest_horizontal")
}

# Definindo os anos únicos para iterar
anos <- sort(unique(part_invest_long$Ano))

# Loop para salvar cada frame como PNG
for (i in seq_along(anos)) {
  # Filtrando os dados para o ano atual
  dados_ano <- part_invest_long[part_invest_long$Ano == anos[i], ]
  
  # Criando o gráfico de barras horizontal
  p <- plot_ly(dados_ano, 
               x = ~Porcentagem, 
               y = ~Tipo_Investidor, 
               color = ~Tipo_Investidor, 
               type = "bar", 
               orientation = 'h',  
               text = ~round(Porcentagem, 1),  
               textposition = "outside",  
               hoverinfo = "text", 
               name = "Investimento por Tipo de Investidor",
               width = 1000,  
               height = 600   
  ) %>%
    layout(
      title = paste("Distribuição de Investimentos por Tipo de Investidor (Ano:", anos[i], ")"),
      xaxis = list(title = "Investimento (%)"),
      yaxis = list(title = "Tipo de Investidor", categoryorder = "total ascending"),  
      showlegend = FALSE,
      bargap = 0.1
    )
  
  # Nome do arquivo PNG com zeros à esquerda
  png_filename <- sprintf("part_invest_horizontal/frame_%03d.png", i)
  
  # Salvando o gráfico como PNG usando Kaleido
  save_image(p, file = png_filename, engine = "kaleido")
}
p
cat("Frames salvos com sucesso na pasta 'part_invest_horizontal'.\n")

# Listando todos os frames 
frames <- list.files("part_invest_horizontal", pattern = "*.png", full.names = TRUE)
frames <- sort(frames)  

# Carregando os frames 
imgs <- image_read(frames)

# Adicionando repetição do último frame 
last_frame <- imgs[length(imgs)]
extra_frames <- rep(last_frame, 30)  
imgs_with_pause <- c(imgs, extra_frames)

# Criando o GIF com animação 
animation <- image_animate(imgs_with_pause, fps = 2)

# Salvando o GIF
image_write(animation, "part_invest_horizontal.gif")

cat("GIF criado com sucesso e salvo como 'part_invest_horizontal.gif'.\n")



# Definindo uma paleta de cores moderna e neutra
color_map <- c(
  "Pessoa.física..Clubes.de.investimentos" = "#4E79A7",  # Azul
  "Institucionais" = "#F28E2B",  # Laranja suave
  "Estrangeiro" = "#E15759",     # Vermelho suave
  "Inst.Financ." = "#76B7B2",    # Verde água
  "Outros" = "#59A14F"           # Verde musgo
)

# Ordenando as categorias dentro de cada ano do maior para o menor valor de investimento
part_invest_long <- part_invest_long %>%
  group_by(Ano) %>%
  arrange(desc(Porcentagem), .by_group = TRUE)

part_invest_long

# Criando o gráfico de barras vertical sem empilhamento e com agrupamento por ano
p <- plot_ly(part_invest_long, 
             x = ~Ano,  
             y = ~Porcentagem, 
             color = ~Tipo_Investidor, 
             colors = color_map,  # Aplicando a nova paleta de cores
             type = "bar", 
             text = ~round(Porcentagem, 1),  
             textposition = "outside",  
             hoverinfo = "text", 
             width = 1000,  
             height = 600  
) %>%
  layout(
    title = "Distribuição de Investimentos por Tipo de Investidor ao Longo dos Anos",
    xaxis = list(title = "Ano", tickvals = unique(part_invest_long$Ano), ticktext = unique(part_invest_long$Ano)),
    yaxis = list(title = "Investimento (%)"),  
    barmode = "group",  # Barras agrupadas por ano
    showlegend = TRUE,
    bargap = 0.3  # Ajustando o espaçamento entre os grupos de barras
  )

# Exibindo o gráfico
p



# Definindo uma paleta de cores moderna e neutra
color_map <- c(
  "Pessoa.física..Clubes.de.investimentos" = "#4E79A7",  # Azul
  "Institucionais" = "#F28E2B",  # Laranja suave
  "Estrangeiro" = "#E15759",     # Vermelho suave
  "Inst.Financ." = "#76B7B2",    # Verde água
  "Outros" = "#59A14F"           # Verde musgo
)

# Ordenando as categorias dentro de cada ano do maior para o menor valor de investimento
part_invest_long <- part_invest_long %>%
  group_by(Ano) %>%
  arrange(desc(Porcentagem), .by_group = TRUE) %>%
  ungroup()

# Convertendo Tipo_Investidor em fator com níveis ordenados para cada ano
part_invest_long <- part_invest_long %>%
  mutate(Tipo_Investidor = factor(Tipo_Investidor, levels = unique(Tipo_Investidor)))

# Criando o gráfico de barras com ggplot2
ggplot(part_invest_long, aes(x = factor(Ano), y = Porcentagem, fill = Tipo_Investidor)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.8)) +  # Barras lado a lado
  scale_fill_manual(values = color_map) +  # Aplicando a paleta de cores
  labs(title = "Distribuição de Investimentos por Tipo de Investidor no Mercado à Vista ao Longo do Tempo",
       x = "Ano",
       y = "Investimento (%)",
       fill = "Tipo de Investidor") +
  geom_text(aes(label = round(Porcentagem, 1)),  # Adicionando os valores nas barras
            position = position_dodge(width = 0.8), 
            vjust = -0.3, size = 3)+
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))  # Inclinação dos rótulos do eixo X para melhor legibilidade



