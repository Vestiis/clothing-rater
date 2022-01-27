from typing import List

import pytest

from src.interpreter import Interpreter

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
        ]
    )
]


@pytest.mark.parametrize("materials_names, label", list(zip(MATERIALS_NAMES, LABELS)))
def test_interpreter_find_materials(
    interpreter: Interpreter, materials_names: List[str], label: str
):
    materials_names = [
        Interpreter._standardize_material_name(material_name)
        for material_name in materials_names
    ]
    materials = interpreter.find_materials(label)
    for material in materials:
        material.names = [
            Interpreter._standardize_material_name(name) for name in material.names
        ]
    for material in materials:
        assert any(name in materials_names for name in material.names)
    for material_name in materials_names:
        assert any(material_name in material.names for material in materials)


@pytest.mark.parametrize("country, label", list(zip(COUNTRIES, LABELS)))
def test_interpreter_find_country(
    interpreter: Interpreter, country: List[str], label: str
):
    found_country = interpreter.find_country(label=label)
    if found_country is not None or country is not None:
        assert Interpreter._standardize_country_name(country) in [
            Interpreter._standardize_country_name(name) for name in found_country.names
        ]
