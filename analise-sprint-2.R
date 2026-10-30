dados <- read.csv("monitoramento_do_hardware.csv",stringsAsFactors = FALSE)

dim(dados)
head(dados)

dados$rede_total <- dados$bytes_recebidos + dados$bytes_enviados

library(ggplot2)
library(corrplot)

dados$rede_total <- dados$bytes_recebidos + dados$bytes_enviados

limite_cpu <- 80
limite_ram <- 85
limite_swap <- 40
limite_rede <- 100000
limite_disco <- 90


# ============================================================
# PORCENTAGEM DE OBSERVAÇÕES EM ALERTA
# ============================================================

alerta_cpu <- dados$porcentagem_cpu > limite_cpu
alerta_ram <- dados$ram_porcentagem > limite_ram
alerta_swap <- dados$swap_porcentagem > limite_swap
alerta_rede <- dados$rede_total > limite_rede
alerta_disco <- dados$disco_porcentagem > limite_disco

percentual_alertas <- data.frame(
  componente = c("CPU", "RAM", "Swap", "Rede", "Disco"),
  percentual = c(mean(alerta_cpu, na.rm = TRUE) * 100,
    mean(alerta_ram, na.rm = TRUE) * 100,
    mean(alerta_swap, na.rm = TRUE) * 100,
    mean(alerta_rede, na.rm = TRUE) * 100,
    mean(alerta_disco, na.rm = TRUE) * 100))

ggplot(percentual_alertas, aes(x = reorder(componente, percentual),
           y = percentual)) +
  geom_col(fill = "steelblue") +
  geom_text(aes(label = paste0(round(percentual, 1), "%")), hjust = -0.2) +
  coord_flip() +
  labs(title = "Porcentagem de observações em estado de alerta",
    x = "Componente",
    y = "Observações em alerta (%)") + theme_minimal()


# ============================================================
# MATRIZ DE CORRELAÇÃO
# ============================================================

componentes <- dados[, c("porcentagem_cpu", 
                         "ram_porcentagem",
                         "swap_porcentagem", 
                         "rede_total")]

correlacoes <- cor(
  componentes,
  method = "spearman",
  use = "complete.obs"
)

corrplot(
  correlacoes,
  method = "color",
  type = "upper",
  addCoef.col = "black",
  tl.col = "black",
  tl.srt = 45,
  number.cex = 0.7
)

# ============================================================
# RELAÇÃO ENTRE CPU E RAM
# ============================================================

ggplot(dados, aes( x = porcentagem_cpu, y = ram_porcentagem)) +
  geom_point( color = "steelblue", alpha = 0.7) +
  geom_smooth(
    method = "loess",
    color = "red",
    se = FALSE
  ) +
  labs(title = "Relação entre utilização da CPU e RAM",
       x = "Utilização da CPU (%)",
       y = "Utilização da RAM (%)") + theme_minimal()
