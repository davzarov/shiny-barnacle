from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = BASE_DIR / "balance_sheets" / "continental"
DATASETS_DIR = BASE_DIR / "datasets"

# local currency directories
LOCAL_DIR = FILES_DIR / "local"
LOCAL_DATASETS_DIR = DATASETS_DIR / "local"
# foreign currency directories
FOREIGN_DIR = FILES_DIR / "foreign"
FOREIGN_DATASETS_DIR = DATASETS_DIR / "foreign"

assets_cols = ["Disponible",
               "Valores Publicos",
               "Creditos S. Financiero",
               "Creditos S. no Financiero",
               "Creditos Diversos",
               "Creditos Vencidos",
               "Inversiones",
               "Bienes de Uso",
               "Cargos Diferidos",
               "Total Activo"]

liabilities_cols = ["Obligaciones S. Financiero",
                    "Obligaciones S. no Financiero",
                    "Diversas",
                    "Provisiones y Previsiones",
                    "Total Pasivo",
                    "Patrimonio",
                    "Capital Social",
                    "Aportes no Capitalizados",
                    "Ajustes al Patrimonio",
                    "Reservas",
                    "Resultados Acumulados",
                    "Resultado del Ejercicio",
                    "Antes de Impuestos",
                    "Impuesto a la Renta",
                    "Total Pasivo y Pratrimonio"]

loss_cols = ["Obligacion S. Financiero",
             "Obligacion S. no Financiero",
             "Valuacion",
             "Incobrabilidad",
             "Servicio",
             "Otras Perdidas Operativas",
             "Extraordinarias",
             "Ajuste de Ejercicios Anteriores",
             "Resultado del Ejercicio",
             "Total"]

profit_cols = ["Creditos Vigentes S. Financiero",
               "Creditos Vigentes S. no Financiero",
               "Creditos Vencidos",
               "Valuacion",
               "Rentas y Diferencia Publicos y Privados",
               "Desafectacion de Previsones",
               "Servicio",
               "Otras Ganancias Operativas",
               "Extraordinarias",
               "Ajuste de Ejercicios Anteriores",
               "Total"]

blacklisted = ["2015_12.pdf",  # -> false positive, orientation is landscape
               "2016_12.pdf",  # -> orientation not landscape, fixed file not opening
               "2017_12.pdf",  # -> false positive, orientation is landscape
               "2018_01.pdf",  # -> text extraction failed, file is scanned
               "2018_10.pdf",  # -> returns 9 not 10
               "2018_02.pdf",  # -> text extraction failed, file is scanned
               "2020_09.pdf",  # -> text extraction failed, file is scanned
               "2021_04.pdf"]  # -> returns 9 not 10
