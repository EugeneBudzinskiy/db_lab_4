import time

from classes import FileArray
from classes import LoggerEngine

from config import DATABASE_NAME
from config import TABLE_NAME
from config import RESULT_PLOT_PATH
from config import TIME_RECORD_PATH

from functions import import_csv
from functions import log_row_count
from functions import create_client
from functions import save_bar
from functions import save_load_time


def get_data_from_database(collection):
    result = collection.aggregate([
        {"$match": {"ukr_test_status": "Зараховано"}},
        {"$group": {
            "_id": {
                "region": "$reg_region_name",
                "year": "$year",
            },
            "avg_score": {
                "$avg": {"$toDouble": "$ukr_score_200"}
            }
        }},
        {"$sort": {'_id.region': 1}}
    ])
    return result


def convert_result(result, cutout_word: str, a_key: str, b_key: str):
    res_dict = dict()
    for el in result:
        region, year, score = el['_id']['region'], el['_id']['year'], el['avg_score']
        region = region.replace(cutout_word, '').strip()
        if region not in res_dict:
            res_dict[region] = dict()
        res_dict[region][year] = score

    labels = list(res_dict.keys())
    a_values, b_values = list(), list()

    for el in labels:
        a_values.append(res_dict[el][a_key])
        b_values.append(res_dict[el][b_key])

    return labels, a_values, b_values


def main():
    file_array = FileArray(
        cols_dict={'student_id': 'CHAR(64)', 'birth': 'INTEGER', 'sex_type': 'CHAR(10)', 'reg_region_name': 'CHAR(64)',
                   'reg_area_name': 'CHAR(64)', 'reg_territory_name': 'CHAR(64)', 'student_type': 'CHAR(100)',
                   'reg_territory_type': 'CHAR(32)', 'class_profile': 'CHAR(48)', 'class_lang': 'CHAR(16)',
                   'eo_name': 'CHAR(256)', 'eo_type': 'CHAR(64)', 'eo_region_name': 'CHAR(64)',
                   'eo_area_name': 'CHAR(64)', 'eo_territory_name': 'CHAR(64)', 'eo_parent_name': 'CHAR(256)',

                   'ukr_test': 'CHAR(32)', 'ukr_test_status': 'CHAR(20)', 'ukr_score_200': 'REAL',
                   'ukr_score_12': 'REAL', 'ukr_score': 'REAL', 'ukr_adapt_scale': 'INTEGER',
                   'ukr_pt_name': 'CHAR(256)', 'ukr_pt_region_name': 'CHAR(64)', 'ukr_pt_area_name': 'CHAR(64)',
                   'ukr_pt_territory_name': 'CHAR(64)',

                   'hist_test': 'CHAR(32)', 'hist_lang': 'CHAR(16)', 'hist_test_status': 'CHAR(20)',
                   'hist_score_200': 'REAL', 'hist_score_12': 'REAL', 'hist_score': 'REAL',
                   'hist_pt_name': 'CHAR(256)', 'hist_pt_region_name': 'CHAR(64)', 'hist_pt_area_name': 'CHAR(64)',
                   'hist_pt_territory_name': 'CHAR(64)',

                   'math_test': 'CHAR(32)', 'math_lang': 'CHAR(16)', 'math_test_status': 'CHAR(20)',
                   'math_score_200': 'REAL', 'math_score_12': 'REAL', 'math_score': 'REAL',
                   'math_pt_name': 'CHAR(256)', 'math_pt_region_name': 'CHAR(64)', 'math_pt_area_name': 'CHAR(64)',
                   'math_pt_territory_name': 'CHAR(64)',

                   'phys_test': 'CHAR(32)', 'phys_lang': 'CHAR(16)', 'phys_test_status': 'CHAR(20)',
                   'phys_score_200': 'REAL', 'phys_score_12': 'REAL', 'phys_score': 'REAL',
                   'phys_pt_name': 'CHAR(256)', 'phys_pt_region_name': 'CHAR(64)', 'phys_pt_area_name': 'CHAR(64)',
                   'phys_pt_territory_name': 'CHAR(64)',

                   'chem_test': 'CHAR(32)', 'chem_lang': 'CHAR(16)', 'chem_test_status': 'CHAR(20)',
                   'chem_score_200': 'REAL', 'chem_score_12': 'REAL', 'chem_score': 'REAL',
                   'chem_pt_name': 'CHAR(256)', 'chem_pt_region_name': 'CHAR(64)', 'chem_pt_area_name': 'CHAR(64)',
                   'chem_pt_territory_name': 'CHAR(64)',

                   'bio_test': 'CHAR(32)', 'bio_lang': 'CHAR(16)', 'bio_test_status': 'CHAR(20)',
                   'bio_score_200': 'REAL', 'bio_score_12': 'REAL', 'bio_score': 'REAL',
                   'bio_pt_name': 'CHAR(256)', 'bio_pt_region_name': 'CHAR(64)', 'bio_pt_area_name': 'CHAR(64)',
                   'bio_pt_territory_name': 'CHAR(64)',

                   'geo_test': 'CHAR(32)', 'geo_lang': 'CHAR(16)', 'geo_test_status': 'CHAR(20)',
                   'geo_score_200': 'REAL', 'geo_score_12': 'REAL', 'geo_score': 'REAL',
                   'geo_pt_name': 'CHAR(256)', 'geo_pt_region_name': 'CHAR(64)', 'geo_pt_area_name': 'CHAR(64)',
                   'geo_pt_territory_name': 'CHAR(64)',

                   'eng_test': 'CHAR(32)', 'eng_test_status': 'CHAR(20)', 'eng_score_200': 'REAL',
                   'eng_score_12': 'REAL', 'eng_dpa_level': 'CHAR(24)', 'eng_score': 'REAL',
                   'eng_pt_name': 'CHAR(256)', 'eng_pt_region_name': 'CHAR(64)', 'eng_pt_area_name': 'CHAR(64)',
                   'eng_pt_territory_name': 'CHAR(64)',

                   'fra_test': 'CHAR(32)', 'fra_test_status': 'CHAR(20)', 'fra_score_200': 'REAL',
                   'fra_score_12': 'REAL', 'fra_dpa_level': 'CHAR(24)', 'fra_score': 'REAL',
                   'fra_pt_name': 'CHAR(256)', 'fra_pt_region_name': 'CHAR(64)', 'fra_pt_area_name': 'CHAR(64)',
                   'fra_pt_territory_name': 'CHAR(64)',

                   'deu_test': 'CHAR(32)', 'deu_test_status': 'CHAR(20)', 'deu_score_200': 'REAL',
                   'deu_score_12': 'REAL', 'deu_dpa_level': 'CHAR(24)', 'deu_score': 'REAL',
                   'deu_pt_name': 'CHAR(256)', 'deu_pt_region_name': 'CHAR(64)', 'deu_pt_area_name': 'CHAR(64)',
                   'deu_pt_territory_name': 'CHAR(64)',

                   'spa_test': 'CHAR(32)', 'spa_test_status': 'CHAR(20)', 'spa_score_200': 'REAL',
                   'spa_score_12': 'REAL', 'spa_dpa_level': 'CHAR(24)', 'spa_score': 'REAL',
                   'spa_pt_name': 'CHAR(256)', 'spa_pt_region_name': 'CHAR(64)', 'spa_pt_area_name': 'CHAR(64)',
                   'spa_pt_territory_name': 'CHAR(64)'},
        added_cols_dict={'year': 'INTEGER'},
        delimiter=';',
        decimal='.',
        nan_value='null'
    )

    file_array.add_file(
        filepath='data/ZNO_2019.csv',
        cols_to_use=['OUTID', 'Birth', 'SEXTYPENAME', 'REGNAME', 'AREANAME', 'TERNAME', 'REGTYPENAME', 'TerTypeName',
                     'ClassProfileNAME', 'ClassLangName', 'EONAME', 'EOTYPENAME', 'EORegName', 'EOAreaName',
                     'EOTerName', 'EOParent',

                     'UkrTest', 'UkrTestStatus', 'UkrBall100', 'UkrBall12', 'UkrBall', 'UkrAdaptScale', 'UkrPTName',
                     'UkrPTRegName', 'UkrPTAreaName', 'UkrPTTerName',

                     'histTest', 'HistLang', 'histTestStatus', 'histBall100', 'histBall12', 'histBall', 'histPTName',
                     'histPTRegName', 'histPTAreaName', 'histPTTerName',

                     'mathTest', 'mathLang', 'mathTestStatus', 'mathBall100', 'mathBall12', 'mathBall', 'mathPTName',
                     'mathPTRegName', 'mathPTAreaName', 'mathPTTerName',

                     'physTest', 'physLang', 'physTestStatus', 'physBall100', 'physBall12', 'physBall', 'physPTName',
                     'physPTRegName', 'physPTAreaName', 'physPTTerName',

                     'chemTest', 'chemLang', 'chemTestStatus', 'chemBall100', 'chemBall12', 'chemBall', 'chemPTName',
                     'chemPTRegName', 'chemPTAreaName', 'chemPTTerName',

                     'bioTest', 'bioLang', 'bioTestStatus', 'bioBall100', 'bioBall12', 'bioBall', 'bioPTName',
                     'bioPTRegName', 'bioPTAreaName', 'bioPTTerName',

                     'geoTest', 'geoLang', 'geoTestStatus', 'geoBall100', 'geoBall12', 'geoBall', 'geoPTName',
                     'geoPTRegName', 'geoPTAreaName', 'geoPTTerName',

                     'engTest', 'engTestStatus', 'engBall100', 'engBall12', 'engDPALevel', 'engBall', 'engPTName',
                     'engPTRegName', 'engPTAreaName', 'engPTTerName',

                     'fraTest', 'fraTestStatus', 'fraBall100', 'fraBall12', 'fraDPALevel', 'fraBall', 'fraPTName',
                     'fraPTRegName', 'fraPTAreaName', 'fraPTTerName',

                     'deuTest', 'deuTestStatus', 'deuBall100', 'deuBall12', 'deuDPALevel', 'deuBall', 'deuPTName',
                     'deuPTRegName', 'deuPTAreaName', 'deuPTTerName',

                     'spaTest', 'spaTestStatus', 'spaBall100', 'spaBall12', 'spaDPALevel', 'spaBall', 'spaPTName',
                     'spaPTRegName', 'spaPTAreaName', 'spaPTTerName'],
        delimiter=';',
        decimal=',',
        encoding='windows-1251',
        nan_value='null',
        value_to_add=[2019]
    )

    file_array.add_file(
        filepath='data/ZNO_2020.csv',
        cols_to_use=['OUTID', 'Birth', 'SEXTYPENAME', 'REGNAME', 'AREANAME', 'TERNAME', 'REGTYPENAME', 'TerTypeName',
                     'ClassProfileNAME', 'ClassLangName', 'EONAME', 'EOTYPENAME', 'EORegName', 'EOAreaName',
                     'EOTerName', 'EOParent',

                     'UkrTest', 'UkrTestStatus', 'UkrBall100', 'UkrBall12', 'UkrBall', 'UkrAdaptScale', 'UkrPTName',
                     'UkrPTRegName', 'UkrPTAreaName', 'UkrPTTerName',

                     'histTest', 'HistLang', 'histTestStatus', 'histBall100', 'histBall12', 'histBall', 'histPTName',
                     'histPTRegName', 'histPTAreaName', 'histPTTerName',

                     'mathTest', 'mathLang', 'mathTestStatus', 'mathBall100', 'mathBall12', 'mathBall', 'mathPTName',
                     'mathPTRegName', 'mathPTAreaName', 'mathPTTerName',

                     'physTest', 'physLang', 'physTestStatus', 'physBall100', 'physBall12', 'physBall', 'physPTName',
                     'physPTRegName', 'physPTAreaName', 'physPTTerName',

                     'chemTest', 'chemLang', 'chemTestStatus', 'chemBall100', 'chemBall12', 'chemBall', 'chemPTName',
                     'chemPTRegName', 'chemPTAreaName', 'chemPTTerName',

                     'bioTest', 'bioLang', 'bioTestStatus', 'bioBall100', 'bioBall12', 'bioBall', 'bioPTName',
                     'bioPTRegName', 'bioPTAreaName', 'bioPTTerName',

                     'geoTest', 'geoLang', 'geoTestStatus', 'geoBall100', 'geoBall12', 'geoBall', 'geoPTName',
                     'geoPTRegName', 'geoPTAreaName', 'geoPTTerName',

                     'engTest', 'engTestStatus', 'engBall100', 'engBall12', 'engDPALevel', 'engBall', 'engPTName',
                     'engPTRegName', 'engPTAreaName', 'engPTTerName',

                     'fraTest', 'fraTestStatus', 'fraBall100', 'fraBall12', 'fraDPALevel', 'fraBall', 'fraPTName',
                     'fraPTRegName', 'fraPTAreaName', 'fraPTTerName',

                     'deuTest', 'deuTestStatus', 'deuBall100', 'deuBall12', 'deuDPALevel', 'deuBall', 'deuPTName',
                     'deuPTRegName', 'deuPTAreaName', 'deuPTTerName',

                     'spaTest', 'spaTestStatus', 'spaBall100', 'spaBall12', 'spaDPALevel', 'spaBall', 'spaPTName',
                     'spaPTRegName', 'spaPTAreaName', 'spaPTTerName'],
        delimiter=';',
        decimal=',',
        encoding='windows-1251',
        nan_value='null',
        value_to_add=[2020]
    )

    # Init database and logger
    logger_engine = LoggerEngine()
    client = create_client()

    # Ref database
    database = client[DATABASE_NAME]
    collection = database[TABLE_NAME]

    # Continues upload the file
    flag = True
    while flag:
        start = time.time()

        exist_flag = TABLE_NAME in database.list_collection_names()
        log_row_count(collection=collection, logger_engine=logger_engine, exist_flag=exist_flag)
        flag = import_csv(collection=collection, file_array=file_array, exist_flag=exist_flag, batch_size=10000)

        end = time.time()
        save_load_time(TIME_RECORD_PATH, start=start, end=end)

    else:
        logger_engine.print_info('File fully loaded!')

    # Get result data
    a_key, b_key = '2019', '2020'
    title = 'Comparisons average score of Ukrainian Language test'
    y_label = 'Average score'

    # Get data from table
    result = get_data_from_database(collection=collection)

    # Save bar plot of results
    labels, a_values, b_values = convert_result(result=result, cutout_word='область', a_key=a_key, b_key=b_key)
    save_bar(filepath=RESULT_PLOT_PATH, labels=labels, a_values=a_values, b_values=b_values, title=title,
             a_label=a_key, b_label=b_key,  y_label=y_label, vertical_labels=True, size_inches=(12, 6))
    logger_engine.print_info('Bar plot is saved!')


if __name__ == '__main__':
    main()
