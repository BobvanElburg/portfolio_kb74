<head>
 <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
</head>

# Welkom!
Op mijn Github-Pages site ter behoeve van het vastleggen van mijn portfolio. 
Ik zal deze site gedurende de loop van het blok KB-74: Applied data science, opbouwen.
Dit portfolio zal dienen als een naslagwerk van mijn uitgevoerde werkzaamheden gedurende 'KB-74', 
waar ik deel heb uitgemaakt van het project *Urbinn*.


## Urbinn?
URBINN, afkorting van URBan INNovations is een LearningLab rondom autonoom rijdend vervoer binnen stedelijke gebieden. 
Binnen URBINN wordt een autonoom rijdend voertuig ontwikkeld dat als basis zal dienen voor onderzoek naar autonoom rijde en de toepassing daarvan binnen een stedelijk gebied. De ontwikkeling hiervan is opgedeeld in meerdere minoren:
* **Applied data science**
* Embedded systems
* Living labs
* Research and innovation
* Robotics and vision design
* Serious gaming

Alle bovengenoemde minoren vallen  onder het Lectoraat Smart Sensor Systems. De ontwikkeling van het voertuig wordt geheel gecoördineerd en gefaciliteerd binnen de Betafactory, te Delft. 

## Wat valt er te vinden in dit portfolio?
De volgende items zullen in ieder geval naar voren komen in mijn portfolio:
* De door mij gegeven presentaties
* Code snippets die ik geschreven heb
* Screenshots van de online courses die ik doorlopen heb. (DataCamp / Coursera)
* De tickets die ik opgelost heb.
* Uitgelichte onderwerpen
* De opdrachten van de bezochte workshops

Verder zal dit lijstje aangevuld worden met:
opgeleverde producten, eigen experimenten, testen, producten, etc. 

## Hoe ga ik dit doen?
Vanwege de incrementele aard van dit portfolio en het overzicht wat daarbij ge*paard* gaat, heb ik ervoor gekozen om per week het portfolio aan te vullen.
Ik zal hierbij aan het einde van de week de belangrijkste gebeurtenissen verzamelen en documenteren en onder het kopje van die week in mijn portfolio stoppen

***

# Het portfolio

***
## Behandelde issues:
###### Te vinden op [GitHub issues](https://github.com/urbinn/urbinn/issues?q=assignee%3Achrisros) voor  toegang graag contact opnemen met @jeroenvuurens.
id  | Beschrijving
--- | -----------------------------------------------------------------------------------
 2  | Het zoeken van bestaande datasets, zoals videobeelden en kaarten verzameld door andere partijen (organisaties/universiteiten) Het in kaart brengen van gebruikte technologieën zoals camera’s, sensoren & tooling.
 22 | Deze week hebben we verschillende projecten met eigen algoritmes (vertakkingen van SLAM (Simultaneous Localisation and Mapping) onderzocht. Criteria opgesteld waar de algortimes aan moeten voldoen. Mogelijke kandidaten geselecteerd waar wij verder mee gaan experimenteren. Uiteindelijke kandidaten: ORB-SLAM2 & SVO.
 31 | Glossary aangemaakt voor het centraal beheren van alle begrippen en hun betekenis.
 34 | Samen met jeroen heb ik gezocht naar de juiste camera voor het het gebruik met stereo-SLAM, uitgekomen op de ZED van stereolabs
 35 | Ik heb de camera calibratie binnen ROS werkend gemaakt, dit maakt het mogelijk elke (stereo) camera te calibreren.
 38 | Zelf een testopstelling gemaakt met twee webcams om als stereo camera footage te gebruiken, zie meer bij 'Stereo camera hack'.
 44 | Geholpen met de installatie van ORB2 SLAM op de datascience server.
 53 | ORB2 installatie in een eigen repository gestopt. 
 55 | Onderzoek gedaan naar object detection papers, de ze papers zijn hier te vinden ## TODO ##
 59 | Documenteren van de data structuur van 'Map' binnen ORB2
 65 | Yolo uitproberen op KITTI, Uit veel papers blijkt echter wel dat YOLO een van de beste kandidaten is op het gebied van real-time object detection en classification. Na een korte orientatie legde ik de focus op 2 kandidaten: Tiny-YOLO && YOLO9000. Na enige tests kwam ik tot de conclussie dat de accuraatheid van beide smaakjes voor ons doeleinde voldoende is. Omdat Tiny-YOLO veel 'lichter' is ligt de verdere focus op Tiny-YOLO. Ook is uit onderzoek gebleken dat op vierkante afbeeldingen de detectie veel beter en sneller verloopt, dus heb ik de afbeeldngen ook opgeknipt in vierkantjes. De resultaten van de tests zijn te vinden in de map [testcases_yolo](testcases_yolo/).
 73 | Ik heb mij bezig gehouden met het bulk inladen van images in de tiny yolo omgeving. Ik heb hierbij gebruik gemaakt van de bestaande hooks uit darknet.py. Hierdoor heb ik door middel van een python script interactie met de C++ core van YOLO en is het mogelijk eenvoudig een bulk afbeeldingen te verwerken. Tevens heb ik een uitbreding gemaakt die zelf de zogenaamde 'bounding boxes' om de herkende objecten heen tekent. ## TODO SCript toevoegen ##
 74 | Van de dataset van ticket #73 is een Zogenaamde 'ground truth' bekend, dit zijn afbeeldingen die door mensen voorzien zijn van labels op de plaatsen waar objecten staan om de grote dataset van kitte 7000+ foto's te controlleren heb ik een script ## TODO ##  geschreven die op basis van de Intersection Over Union de false positives van TinyYolo bepaald. De uitkomst was 0.14% false positives met een IOU van >50%
 76 | [Repository]( www.github.com/urbinn/yolo) ingericht met daarin YOLO zodat dit eenvoudig uitgerold kan worden. 
 83 | Klassen vastgesteld welke we in onze eigen trainings dataset willen hebben, zodat we YOLO kunnen trainen op het herkennen van deze klassen 
 90 | Samen met Nektarios met de nieuwe ZED Stereocamera beelden geschoten in slinger zodat deze gebruikt kunnen worden voor het evalueren van ORB SLAM
 92 | Calibratie uitgevoerd van de nieuwe camera 
 93 | Samen met Jeroen en Kevin gewerkt aan een werkende training configuratie van Darknet en YOLO dit om te kijken of we zelf een yolo instantie konden trainen, dit bleek moeilijk maar succesvol
 94 | 


## Presentaties:
###### Te vinden in [presenaties](presentaties/)
 Presentatie  | Beschrijving
------------- | -----------------------------------------------------------------------------------
[Week 1](presentaties/week_1.pdf) | Ik heb samen met Nektarios de presentatie van deze week voorbereid en uitgevoerd.
[Week 2](presentaties/week_2.pdf) | Ik heb samen met Nektarios de presentatie van deze week voorbereid en uitgevoerd.
[Week 4](presentaties/week_4.pdf) | In verband met ziekte heb ik samen met Kevin de presentatie van deze week uitgevoerd.
[Week 5](presentaties/week_5.pdf) | In verband met ziekte heb ik samen met Daniello de presentatie van deze week uitgevoerd.


## Scripts:
###### Te vinden in [scripts](scripts/)
 Script  | Beschrijving
------------- | -----------------------------------------------------------------------------------
[Week 1](script/) | 
[Week 2](script/) | 
[Week 4](script/) | 
[Week 5](script/) | 


## Uitgelichte onderwerpen:

### Stereo camera hack:
In deze week ben ik vooral bezig geweest met het maken van en setup voorzien van 2 losse webcams, welke door middel van ROS (Robot Operating System) i.s.m. usb_cam stereo beelden konden opnemen (te zien in de onderstaande afbeelding). Hoewel het experiment redelijk geslaagd was, was het niet mogelijk deze beelden om te zetten in een accurate pointcloud in ORB-slam.

![Camera set-up](images/camera_setup.svg "Camera set-up")


### Testen YOLO varianten:
De  software is zeer slecht gedocumenteerd, uit veel papers blijkt echter wel dat YOLO een van de beste kandidaten is op het gebied van real-time object detection en classification. Na een korte orientatie legde ik de focus op 2 kandidaten: Tiny-YOLO && YOLO9000.
Na enige tests kwam ik tot de conclussie dat de accuraatheid van beide smaakjes voor ons doeleinde voldoende is. Omdat Tiny-YOLO veel 'lichter' is ligt de verdere focus op Tiny-YOLO.
Ook is uit onderzoek gebleken dat op vierkante afbeeldingen de detectie veel beter en sneller verloopt.
De resultaten van de tests zijn te vinden in de map [testcases_yolo](testcases_yolo/). 


### Sequence van afbeeldingen, uitvoer van TinyYOLO:
Ik heb mij bezig gehouden met het bulk inladen van images in de tiny yolo omgeving. Ik heb hierbij gebruik gemaakt van de bestaande hooks uit darknet.py. Hierdoor heb ik door middel van een python script interactie met de C++ core van YOLO en is het mogelijk eenvoudig een bulk afbeeldingen te verwerken. Tevens heb ik een uitbreding gemaakt die zelf de zogenaamde 'bounding boxes' om de herkende objecten heen tekent, tevens wordt deze informatie plain text in een JSON opgeslagen.
Hieronder staat een geanimeerde afbeelding van een reeks van 200 achtereenvolgende foto's welke zij bewerkt door middel van mijn script.
![0-200_sequence.gif](images/0-200_sequence.gif "Sequence gif")

