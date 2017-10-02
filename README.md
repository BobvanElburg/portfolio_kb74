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
* De opdrachten van de bezochte workshops

Verder zal dit lijstje aangevuld worden met:
opgeleverde producten, eigen experimenten, testen, producten, etc. 

## Hoe ga ik dit doen?
Vanwege de incrementele aard van dit portfolio en het overzicht wat daarbij ge*paard* gaat, heb ik ervoor gekozen om per week het portfolio aan te vullen.
Ik zal hierbij aan het einde van de week de belangrijkste gebeurtenissen verzamelen en documenteren en onder het kopje van die week in mijn portfolio stoppen

***

# Het portfolio

***

## Week 1
###### 28-08-2017

### Literatuur onderzoek:
Het zoeken van bestaande datasets, zoals videobeelden en kaarten verzameld door andere partijen (organisaties/universiteiten)
Het in kaart brengen van gebruikte technologieën zoals camera’s en sensoren. Ook is gekeken naar tooling die gebruikt/gemaakt is is om de sensoren en hun data uit te lezen.

### Locatie onderzoek:
Ook zijn wij naar Delft geweest om het gebied te verkennen en om camerabeelden vast te leggen van bijzondere situaties die kunnen voorkomen. Dit is belangrijk aangezien de auto op dit soort situaties foutloos moet reageren

### Presentatie:
Ik heb samen met Nektarios de [presentatie](presentaties/week_1.pdf) van deze week voorbereid en uitgevoerd.

#### Issues: 2

***

## Week 2
###### 04-09-2017

### Implementatie onderzoek:
Deze week hebben we verschillende projecten met eigen algoritmes (vertakkingen van SLAM (Simultaneous Localisation and Mapping) onderzocht.
Criteria opgesteld waar de algortimes aan moeten voldoen.
Mogelijke kandidaten geselecteerd waar wij verder mee gaan experimenteren.
Uiteindelijke kandidaten:
* ORB-SLAM2 
* SVO

### Implementatie:
Geselecteerde kandidaten (ORB-SLAM2, SVO) zijn geïnstalleerd
Niet altijd makkelijk; projecten zijn vaak incompleet
Weinig documentatie; Trial-and-error

### Presentatie:
Ik heb samen met Nektarios de [presentatie](presentaties/week_2.pdf) van deze week voorbereid en uitgevoerd.

#### Issues: 22, 31, 38

*** 

## Week 3
###### 11-09-2017

### Camera Selectie:
Samen met jeroen heb ik gezocht naar de juiste camera voor het het gebruik met stereo-SLAM, uitgekomen op de ZED van stereolabs

### Camera calibratie:
Ik heb de camera calibratie binnen ROS werkend gemaakt, dit maakt het mogelijk elke (stereo) camera te calibreren.

#### Issues: 35

***

## Week 4
###### 18-09-2017

### ORB-SLAM2 geïnstalleerd op de Jupyterhub. 
Eigen dataset gemaakt (Slinger). (meerder malen rondgelopen en gefilmd, eerste filmpje was onstabiel)
Kalibratie van een camera. (met camera calibrator is de camera gekalibreerd aan de hand van een schaakboord. Die een output bestand geeft met de juiste kalibratie settings die gebruikt kunnen worden in de ORB-SLAM2 open source)
Pointcloud opslaan (gelukt met bijgeleverde example)


### Stereo camera hack:
In deze week ben ik vooral bezig geweest met het maken van en setup voorzien van 2 losse webcams, welke door middel van ROS (Robot Operating System) i.s.m. usb_cam stereo beelden konden opnemen (te zien in de onderstaande afbeelding). Hoewel het experiment redelijk geslaagd was, was het niet mogelijk deze beelden om te zetten in een accurate pointcloud in ORB-slam.

![Camera set-up](images/camera_setup.jpg "Camera set-up")

### Presentatie:
In verband met ziekte heb ik samen met Kevin de [presentatie](presentaties/week_4.pdf) van deze week uitgevoerd.

#### Issues: 53, 44

***

## Week 5
###### 25-09-2017

Veel losse werkzaamheden uitgevoerd, druk bezig geweest met Coursera.
ORB-SLAM 2 code gedocumenteerd
Begonnen met verkenning object recogntition

### Presentatie:
In verband met ziekte heb ik samen met Daniello de [presentatie](presentaties/week_5.pdf) van deze week uitgevoerd.

#### Issues: 55, 59

***
## Week 6
###### 02-10-2017

#### Issues: 65

***

## Week 7
- TODO

#### Issues: 73

***
## Week 8
- TODO

***
## Week 9
- TODO

***
## Week 10
- TODO

***
## Week 11
- TODO

***
## Week 12
- TODO

***
## Week 13
- TODO

***
## Week 14
- TODO

***
## Week 15
- TODO

***
## Week 16
- TODO

***
## Week 17
- TODO

***
## Week 18
- TODO

***




 
