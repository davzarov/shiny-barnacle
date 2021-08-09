from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "balance_sheets" / "continental"
DATASETS_DIR = BASE_DIR / "datasets"

# local currency directories
LOCAL_DIR = FILES_DIR / "local"
LOCAL_DATASETS_DIR = DATASETS_DIR / "local"
# foreign currency directories
FOREIGN_DIR = FILES_DIR / "foreign"
FOREIGN_DATASETS_DIR = DATASETS_DIR / "foreign"

months_es = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SEPTIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12
}

months_en = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12
}

assets_dict = {
    "from": None,
    "to": "CARGOS DIFERIDOS",
    "cols": ["Disponible",
             "Valores Publicos",
             "Creditos S. Financiero",
             "Creditos S. no Financiero",
             "Creditos Diversos",
             "Creditos Vencidos",
             "Inversiones",
             "Bienes de Uso",
             "Cargos Diferidos"]
}

liabilities_dict = {
    "from": None,
    "to": "PROVISIONES Y PREVISIONES",
    "cols": ["Obligaciones S. Financiero",
             "Obligaciones S. no Financiero",
             "Diversas",
             "Provisiones y Previsiones"]
}

equity_dict = {
    "col_0": {
        "from": "AJUSTES AL PATRIMONIO",
        "to": "RESULTADOS ACUMULADOS"
    },
    "col_1": {
        "from": "CAPITAL SOCIAL",
        "to": "APORTES NO CAPITALIZADOS"
    },
    "cols": ["Capital Social",
             "Aportes no Capitalizados",
             "Ajustes al Patrimonio",
             "Reservas",
             "Resultados Acumulados"]
}

exercise_dict = {
    "from": "Resultado del ejercicio antes del impuesto",
    "to": "Menos: Impuesto a la renta",
    "cols": ["Antes de Impuestos",
             "Impuesto a la Renta"]
}

# using default extraction strategy
profit_loss_dict = {
    "from": "PERDIDAS POR OBLIGACION POR INTERMEDIACION FINANCIERA S. FINANCIERO",
    "to": "AJUSTES DE RESULTADOS DE EJERCICIOS ANTERIORES",
    "loss_cols": ["Obligacion S. Financiero",
                  "Obligacion S. no Financiero",
                  "Valuacion",
                  "Incobrabilidad",
                  "Servicio",
                  "Otras Perdidas Operativas",
                  "Extraordinarias",
                  "Ajuste de Ejercicios Anteriores"],
    "profit_cols": ["Creditos Vigentes S. Financiero",
                    "Creditos Vigentes S. no Financiero",
                    "Creditos Vencidos",
                    "Valuacion",
                    "Rentas y Diferencia Publicos y Privados",
                    "Desafectacion de Previsones",
                    "Servicio",
                    "Otras Ganancias Operativas",
                    "Extraordinarias",
                    "Ajuste de Ejercicios Anteriores"]
}

profit_dict = {
    "cols": ["Creditos Vigentes S. Financiero",
             "Creditos Vigentes S. no Financiero",
             "Creditos Vencidos",
             "Valuacion",
             "Rentas y Diferencia Publicos y Privados",
             "Desafectacion de Previsones",
             "Servicio",
             "Otras Ganancias Operativas",
             "Extraordinarias",
             "Ajuste de Ejercicios Anteriores"]
}

loss_dict = {
    "cols": ["Obligacion S. Financiero",
             "Obligacion S. no Financiero",
             "Valuacion",
             "Incobrabilidad",
             "Servicio",
             "Otras Perdidas Operativas",
             "Extraordinarias",
             "Ajuste de Ejercicios Anteriores"]
}
