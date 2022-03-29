from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.api import get_application
from src.interpreter import Interpreter, get_interpreter
from src.words_matcher.words_matcher import get_words_matcher


@pytest.fixture()
def interpreter() -> Interpreter:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    yield get_interpreter(words_matcher=get_words_matcher())


@pytest.fixture()
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh app on each test case.
    """
    _app = get_application()

    def _check_security():
        return None

    # _app.dependency_overrides[check_security] = _check_security

    yield _app


@pytest.fixture()
def client(app: FastAPI) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    with TestClient(app=app) as client:
        yield client


COUNTRIES, MATERIALS_NAMES, LABELS = [
    list(x)
    for x in zip(
        *[
            ("china", ["coton"], "cotton 100% china"),
            # https://storage.googleapis.com/public-labels/dc63aa8c-8057-40a6-845b-63455d510f13.JPG
            (
                "turkey",
                ["Acrylique"],
                "KEEP AWAY\nFROM FIRE\n11267810\nF100299\n100% ACRYLIC\n100% ACRYLIQUE\n100% ACRİLICO\n100% ACRYL\nMADE IN TURKEY\nSCAN HERE FOR\nMORE INFORMATION\nRECLAIME\nMINIAGE\nEIGHT PAw\nPROJECTS LIMITED\n",
            ),
            # https://storage.googleapis.com/public-labels/8db0179c-531c-4e36-9a71-8d738215d908.JPG.
            # https://storage.googleapis.com/public-labels/cbcaf9f6-0558-4736-b512-93e8399e288e.JPG
            (
                "vietnam",
                ["elasthanne", "viscose", "polyester"],
                "79% poliéster - polyester - poliestere - noAYEETEPAE- RUIZFIL-poliester - RMF- A.\nwsalg - polièster - poliesterra\n15% viscosa - viscose - BIEKOZH- L-aY-viskose - viskoza - T - HAJA- jaSu - biskosa\n6% elastano - élasthanne - elastane - elastaan - elastan - EAAETINH- USLIY-2- 92AE. /\naliull - elastà - elastanoa\n EURM USAM MEX 28\nMADE IN VIETNAM\nl-pondeter-pol\n% elastano-lanthanne\nEOL\n",
            ),
            # https://storage.googleapis.com/public-labels/35e8cf86-10ab-4226-8b5d-6ae0310c6033.JPG
            # https://storage.googleapis.com/public-labels/7862e023-3d52-4657-ab88-9e8d17b32ee6.JPG
            (
                "Sri Lanka",
                ["polyester"],
                "DE MIT AHNLICHEN FARBEN\nWASCHEN\n100% POLYESTER\nE PESE KOOS SARNAST VÄRVI\nREEETEGA\n100% POLGESTER\nES LAVAR CON PRENDAS DE\nCOLOR PARECIDO\n100% poliester\nA PESTAAN SAMANVARISTEN\nKANSSA\n100% POLYESTERIA\nFR LAVER AVECCOULEURS\nSIMILAIRES\n100% POLYESTER\nIT LAVARE CON COLORI SIMILI\n100% POLIESTERE\nNE WASSEN HET DEZELFDE\nKLEUREN\n100% POLYESTER\nPL PRACZPODOBNYMI\nKOLORAM\n100% POLIESTER\nRO SPALAȚICU CULORI\nSIMILARU\n RIVER ISLAND\n5057110902866\n794358\nUK\nEUR\n10\n36\nUS\nMade in Sri Lanka\nG7\nFE012\nRIVERISLAND.COM\nRiver Island Clothing Co Ltd\nChelsea House, Westgate\nws IDR. U\n",
            ),
            # https://storage.googleapis.com/public-labels/0ab52eac-acf8-4fc2-a5d0-1af2dd2972c9.JPG
            (
                None,
                ["Polyamide", "Elasthanne"],
                "에스터/ Dentelle/Lace/Encaje/Kantwerk/ Spitze/Koronka/Krajka/KpyxeBo/ Jy TEPizzolal0IA/ Neriniai 90%polyamide/polyamide/ poliamida/polyamide/polyamid/ poliamid/polyamid/nonwamna/ d poliammidel 플리아미드/ poliamidinis 10%elasthannelelastanel elastano/elastaanlelasthan/ elastan/elastan/anactaH/ lelastane! 엘라스테인 / elastanas",
            ),
            # https://storage.googleapis.com/public-labels/9ac3dbf4-2434-4c58-9a69-49b877b5e470.JPG
            # https://storage.googleapis.com/public-labels/bfb9c540-b274-4a03-a833-96b990d811df.JPG
            (
                "bulgaria",
                ["polyester", "laine", "elasthanne", "viscose"],
                "FR\nTissu principal\n56% polyester\n41% laine\n3% elasthanne\n100% viscose\nDoublure\nGB\nUS\nMain fabric\n56% polyester\n41% wool\n3% elastane\n100% viscose\nLining\nES\nTejido principal\n58% poliéster\n41% lana\n3% elastano\n100% viscosa\nForro\nDE\nHauptstoff\n56% polyester\n41% wolle\n3% elasthan\n100% viskose\nFutter\nNL\nHoofdstof\n56% polyester\n41% wol\n3% elastaan\n100% viscose\nVoering\nIT\nTessuto\nprincipale\n56% pollestere\n41% lana\n3% elastam\n100% viscosa\nFodera\nSE\nHuvudtyg\n56% polyester\n41% ylle\n3% elastan\n100% viskos\nFoder\nDK\nHovedstof\n50% polyester\n41% uld\n3% olastan\n100% viekose\nFor\nRU\nnonsaorep\nPT\nTecido principal\n50% poloster\n41% ia\n3% elastano\n100% viscose\nForro\n gje\nMADE INBULGARIA\n",
            ),
            # https://storage.googleapis.com/public-labels/04e26266-ff14-4645-af60-e07fe9dddede.JPG
            # https://storage.googleapis.com/public-labels/ebaf391d-db74-415b-8e85-df085e0840a0.JPG
            (
                "sri lanka",
                ["polyester"],
                "如四 不可\nDry flat.Cool iron on\nreverse.Wash inside out.\nHandle this garment with\nextreme care. Wash with\nsimilar colours. Sécher à\nplat.Repasser sur l'envers\nà fer doux.Laver à l'envers.\nManipuler cet article avec\nle plus grand soin.Laver\navec des couleurs\nsemblables.\nMAIN / HUVUDDEL /\nHOOFDDEEL/\nPRINCIPAL / HAUPTSTOFF:\n100% Polyester / Polyester/\nPolyester /Polyester / Polyester.\nRecommended care for this garment\ngreenearthcleaning.com/stores\nComment prendre soin de ce\nvêtement\ngreenearthcleaning comletere\n RIVER 13I\n5057111150655\n792613\nUK 10\nEUR 36\nUS 6\nMade in Sri Lanka\nG8\nFE012\nRIVERISLAND.COM\nRiver Island Clothing Co Ltd\nChelsea House, Westgate,\nLondon, W5 1DR, UK\n",
            ),
            # https://storage.googleapis.com/public-labels/04e26266-ff14-4645-af60-e07fe9dddede.JPG
            # https://storage.googleapis.com/public-labels/ebaf391d-db74-415b-8e85-df085e0840a0.JPG
            (
                "sri lanka",
                ["polyester"],
                "如四 不可\nDry flat.Cool iron on\nreverse.Wash inside out.\nHandle this garment with\nextreme care. Wash with\nsimilar colours. Sécher à\nplat.Repasser sur l'envers\nà fer doux.Laver à l'envers.\nManipuler cet article avec\nle plus grand soin.Laver\navec des couleurs\nsemblables.\nMAIN / HUVUDDEL /\nHOOFDDEEL/\nPRINCIPAL / HAUPTSTOFF:\n100% Polyester / Polyester/\nPolyester /Polyester / Polyester.\nRecommended care for this garment\ngreenearthcleaning.com/stores\nComment prendre soin de ce\nvêtement\ngreenearthcleaning comletere\n RIVER 13I\n5057111150655\n792613\nUK 10\nEUR 36\nUS 6\nMade in Sri Lanka\nG8\nFE012\nRIVERISLAND.COM\nRiver Island Clothing Co Ltd\nChelsea House, Westgate,\nLondon, W5 1DR, UK\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_9182.HEIC
            (
                "china",
                ["laine"],
                "EXTRA FINE MERINO WOOL\nLANE MERINOS EXTRA FINE\nLANA MERINO EXTRA FINE\nGap\nXS/TP\nMADE IN\nCHINA\n100%\nMERNG WOOL\nLAINE MiNDS\nLANA MERING\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_4251.HEIC
            (
                "portugal",
                ["coton bio"],
                "100% coton bio\nsans pesticides\net biodégradable\ntricoté au\nPortugal\nlavage machine autorisé\npas de séchage en machine\nnettoyage à l' eau autorisé\nrepassage moyen autorisé\nbe cool\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_4243.HEIC
            (None, ["laine"], "OCTOBRE EDITIONS 100% LAINE EXTRAFINE EXTRAFINE WOOL"),
            # https://storage.googleapis.com/public-labels/IMG_8981.HEIC
            (
                "Bangladesh",
                ["coton"],
                "EUR M\nM\nUS\nCA M\nCN 175/100A\nMX M\nMade in Bangladesh\nFabriqué en Bangladesh\nHecho en Bangladesh\nO/N 109517\nP/N 0513699 2\nLC TVMOV\nC回X区AO\n40\nclevercare.info\nGB 100% COTTON.\nCz 100% BAVLNA\nDE 100% BAUMWOLLE\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_58024B7D470B-1.jpeg
            (
                "china",
                ["acrylique"],
                "UK 10\nEU 38\nUS\n08784443\nF101068\n100% ACRYLIC\n100% ACRYLIQUE\n100% ACRILICO\n100% ACRYL\nMADE IN CHINA\nPLEASE SCAN ME FOR\nTRANSLATIONS\nASOS\nasos.com Ltd\n",
            ),
            # "https://storage.googleapis.com/public-labels/IMG_9186.HEIC"
            (
                "bangladesh",
                ["POLYESTER", "ELASTANE", "ACRYLIQUE"],
                "FABRICADO EN BANGLADESH/\nFABRICADO NA BANGLADECHE I\nHERGESTELLT IN BANGLADESCH/\nFABRIQUÉ EN BANGLADESH\nGEPRODUCEERD IN BANGLADESH/\nPRODOTTO IN BANGLADESH/\nWYPRODUKOWANO W\nBANGLADESZUI\nIZDELANO V BANGLADESU/\nVYROBENO V BANGLADÉSI\nA'AX\n國 的。\n30\n30C\n72% ACRYLIC / ACRÍLICO/\nACRYL/ ACRYLIQUE /\nACRILICO / AKRYLI AKRIL\n25% POLYESTER / POLIÉSTER/\nPOLIESTERE / POLIESTER\n3% ELASTANE / ELASTANO\nELASTHAN / ÉLASTHANNE\nELASTAAN / ELASTAN\nCOLOU\nCOLUR\nAR AS\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_9188.HEIC
            (
                "Bangladesh",
                ["Organic Cotton", "Polyester"],
                "Medew\nOrgaly GrowCo\ncertifed by Con\nCertificetion CUS19434\nMade in Bangladesh\nSTSW049\n85% Organic Cotton/\nCoton Biologique / Bio-Katoen/\nBio-Baumwolle / Cotone Bilogico/\nAlgodón Orgánico /\nAlgodao Orgânico\n15% Polyester /\nPoliestere / Poliéster\nWash similar colours together.\nno ironing on print,\nwash and iron inside out\n30\nSo06\natent\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_A1881ADFD8B3-1.jpeg
            (
                "italie",
                ["silk"],
                "SETA - SOIE\nSILK - SEIDE\n100%\nYVES SAINT LAURENT\nMADE IN ITALY\n",
            ),
            #
            (
                "jordanie",
                ["coton"],
                "UREN\nIALPH LAUREN\nMADE IN\nJORDAN\nFABRIQUÉ EN\nJORDANIE\n100%\nCOTTON/\nCOTON\nEXCLUSIVE OF\nDECORATION/\nEXCLUSIF\nDE LA\nDÉCORATION\n",
            ),
            # https://storage.googleapis.com/public-labels/20220306_141430.jpg
            # https://storage.googleapis.com/public-labels/20220306_141447.jpg
            (
                "china",
                ["COTTON", "POLYESTER", "recycled cotton"],
                " adidas\nHoogoorddreef 9a\nAmsterdam 1101 BA\nThe Netherlands\nMADE IN CHINA\nFABRIQUÉ EN CHINE\nFABRICADO EN CHINA\nFABRICADO NA CHINA\nGYÁRTVA: KÍNA\nПРОИЗВЕДЕНО В КИТАЙ\nСДЕЛАНО В КИТАЕ\nPROIZVEDENO U KINI\nÇİN'DE İMAL EDİLMİŞTİR.\nҚЫТАЙДА ЖАСАЛҒАН\nPROIZVĖDENO U KINI\nFABRICAT ÎN CHINA\nall: Laill al\nRN# 88387 CA# 40312\nX回aQ\n40\nUS/\nUK: MACHINE WASH WARM/ DO NOT\nBLEACH/ DO NOT TUMBLE DRY/ COOL\nIRON IF NEEDED/DO NOT DRY CLEAN\nDO NOT USE FABRIC SOFTENER/USE\nMILD DETERGENT ONLY/WASH WITH\nLIKE COLORS/DO NOT IRON MOTIF\nD: KEINEN WEICHSPUELER VERWENDEN/\nBITTE FEINWASCHMITTEL VERWENDEN/\nMIT GLEICHEN FARBEN WASCHEN/\nMOTIV BITTE NICHT BUEGELN\nF:\nNE PAS UTILISER D'ASSOUPLISSEUR/\nUTILISER UN DÉTERGENT DOUX/LAVER\n HOOD LINING: 58% COTTON/\n27% POLYESTER (RECYCLED/\n15% COTTON (RECYCLED)\nUK: MAIN MATERIAL: 58% COTTON/\n27% POLYESTER (RECYCLED)y/\n15% COTTON (RECYCLED)/\nHOOD LINING: 58% COTTON/\n27% POLYESTER (RECYCLED)/\n15% COTTON (RECYCLED)\nD: HAUPTMATERIAL:\n58% BAUMWOLLE/27% POLYESTER\n(RECYCLED/15% BAUMWOLLE\n(RECYCLED/KAPUZENFUTTER:\n58% BAUMWOLLE/27% POLYESTER\n(RECYCLED)/15% BAUMWOLLE\n(RECYCLED)\nF: MATIERE PRINCIPALE: 58% COTON/\n27% POLYESTER (RECYCLÉ/\n15% COTON (RECYCLÉJ\nDOUBLURE CAPUCHE: 58% COTON/\n27% POLYESTER (RECYCLÉ/\n15% COTON (RECYCLÉ)\nE: MATERIAL PRINCIPAL:\n58% ALGODÓN/27% POLIESTER\n(RECICLADO15% ALGODÓN\n(RECICLADO)/FORRO CAPUCHA:\n58% ALGODÓN/27% POLIESTER\n(RECICLADO/15% ALGODÓN\n(RECICLADO)\nP: MATERIAL PRINCIPAL:\n58% ALGODĀO/27% POLIÉSTER\n(RECYCLED)15% ALGODÃO\n(RECYCLEDVFORRO DO CAPUZ:\n58% ALGODÃO/27% POLIÉSTER\n(RECYCLEDY15% ALGODÃO\n(RECYCLED)\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_5459.JPEG
            # https://storage.googleapis.com/public-labels/IMG_5460.JPEG
            (
                "poland",
                ["cotton"],
                " PONFRY\nHE OTEMBAT\nLEMDEPATYPE\nMAKCHMYM 110C\nXHM-4RCTKA BCEM\nPACTROPHTERAM\n30^C水洗\n不可潮白\n不可转篮干燥\nLAVER ETREPASSER SUR\nL'ENVERS WASH AND\nIRON INSIDE OUT\nSECHAGE SUR CINTRE\nDRY ON HANGER\nRN 139569\nMADE IN\nPOLAND\nTHE KOOPLED PRODUCION\n11 RUE DE PRONY\n017PARIS FRANCE\n WHI01\nC018445\nTHE KOOPLES\nPARIS\nEXTERIEUR-\nOUTSHELL- EXTERIOR-\nBHEWHAA HACTE\n100%COTON COTTON-\nALGODÓN-\nO巴 又网\nLAVAGE A 30°C\nBLANCHIMENT INTERDIT\nSECHAGE EN TAMBOUR\nINTERDIT\nREPASSAGE 110°C MAX\nNETTOYAGE A SEC TOUS\nSOLVANTS NORMAUX\nWASH AT 30'C\nDO NOT BLEACH\n0O NOT TUMBLE DRY\nON LOW HEAT\n(5.0\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_5453.JPEG
            (
                "china",
                ["laine", "NYLON"],
                " Gap\nMADE WITH LAMBSWOOL\nCONTIENT DE LA LAINE D'AGNEAU\nREALIZZATO IN LANA DI AGNELLO\nS/P\nMADE IN\nCHINA\n52%\nLAMBS'WOOLA\nLAINE\nD'AGNEAU/\nIG VNYT\nAGNELLO\n484 NYLON\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_5447.JPEG
            (
                "china",
                ["cotton"],
                " MADE IN CHINA\nFABRIQUE EN CHINE\nHECHO EN CHINA\nCINDE URETILMISTIR\n100% COTTON/COTON/ALGODON!\nALGODÃO/BAUMWOLLE/COTONE\nPAMUK\nEXCLUSIVE OF DECORATIONELASTIC\nSAUF DÉCORATION/ELASTIQUE\nELASTIK HARICTIR\nUS\n回瓜百品\n40C\nEU\n回人区 O\nWASH DARK COLORS SEPARATELY\nREMOVE PROMPTLY, RESHAPE\nTO SIZE, DRY FLAT IN SHADE\nVERSO/AL REVERSO\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_5484.JPEG
            (
                "china",
                ["nylon"],
                " SHELL 00 NLON\nYADD ING\n8 DOWN\n10% FEATHER\nNE 00 NYL ON\nLININ\n*A BATHING APE\nNOWHERE CO. LTD.\n03 (5772) 2524\nWWWRAP COM\nMADE IN CHINA\n",
            ),
            # https://storage.googleapis.com/public-labels/IMG_5485.JPEG
            (
                "china",
                ["polyester"],
                " 19504104-01)\n-005A-06B\nMADE IN CHINA\nFABRIQUE EN CHINE\nHERGESTELLT IN CHINA\nFABRICADO EN CHINA\nGEMAAKT IN CHINA\nYERKAD I KINA\nESTILLET I KINA.\nRICATO IN CN\nPOLYESTER\nPOLYESTER\n100\nPOLYESTER\n100%\nPOLIESTER\n100%\nPOLYESTER\n100%\nPOLYESTER\n100%\nPOLYESTER\nPOLIESTERE\n",
            ),
        ]
    )
]
