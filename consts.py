months_es = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SETIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12
}

assets_cols = ["Disponible",
               "Valores Publicos",
               "Creditos S. Financiero",
               "Creditos S. no Financiero",
               "Creditos Diversos",
               "Creditos Vencidos",
               "Inversiones",
               "Bienes de Uso",
               "Cargos Diferidos"]

liabilities_cols = ["Obligaciones S. Financiero",
                    "Obligaciones S. no Financiero",
                    "Diversas",
                    "Provisiones y Previsiones"]

equity_cols = ["Capital Social",
               "Aportes no Capitalizados",
               "Ajustes al Patrimonio",
               "Reservas",
               "Resultados Acumulados"]

exercise_cols = ["Antes del Impuesto",
                 "Despues de Impuesto"]

loss_cols = ["Obligacion S. Financiero",
             "Obligacion S. no Financiero",
             "Valuacion",
             "Incobrabilidad",
             "Servicio",
             "Otras Perdidas Operativas",
             "Extraordinarias",
             "Ajuste de Ejercicios Anteriores"]

profit_cols = ["Creditos Vigentes S. Financiero",
               "Creditos Vigentes S. no Financiero",
               "Creditos Vencidos",
               "Valuacion",
               "Rentas y Diferencia Publicos y Privados",
               "Desafectacion de Previsones",
               "Servicio",
               "Otras Ganancias Operativas",
               "Extraordinarias",
               "Ajuste de Ejercicios Anteriores"]

assets_dict = {
    "from": None,
    "to": "CARGOS DIFERIDOS"
}

liabilities_dict = {
    "from": None,
    "to": "PROVISIONES Y PREVISIONES"
}

equity_dict_0 = {
    "from": "AJUSTES AL PATRIMONIO",
    "to": "RESULTADOS ACUMULADOS"
}

equity_dict_1 = {
    "from": "CAPITAL SOCIAL",
    "to": "APORTES NO CAPITALIZADOS"
}

exercise_dict = {
    "from": "Resultado del ejercicio antes del impuesto",
    "to": "Menos: Impuesto a la renta"
}

profit_loss_dict = {
    "from": "PERDIDAS POR OBLIGACION POR INTERMEDIACION FINANCIERA S. FINANCIERO",
    "to": "AJUSTES DE RESULTADOS DE EJERCICIOS ANTERIORES"
}
