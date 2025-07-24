from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cabinet_digital.models import Integrator, Software, Company
import re

class Command(BaseCommand):
    help = 'Import integrators from integrators.md file'

    def handle(self, *args, **options):
        integrators_data = [
            {
                'name': '1Life',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                1Life est un intégrateur ERP dédié à l'industrie, acquis par Visiativ. L'entreprise se concentre sur la planification de la production pour les entreprises manufacturières et a accompagné plus de 1 000 PME industrielles pendant plus d'une décennie. En 2022, 1Life a généré un chiffre d'affaires de 10 millions d'euros, dont la moitié provenait de services de conseil à valeur ajoutée et l'autre moitié d'activités logicielles récurrentes, de maintenance et d'abonnements.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Intégration ERP pour la Fabrication :</strong> Expertise approfondie dans le déploiement et l'optimisation de solutions ERP spécifiquement adaptées aux processus industriels et à la planification de la production</li>
                <li><strong>Planification de la Production :</strong> Spécialisation fondamentale pour les entreprises manufacturières</li>
                <li><strong>Services de Conseil :</strong> Une part significative de leur chiffre d'affaires provient de services de conseil à valeur ajoutée</li>
                <li><strong>Expertise Digitale pour l'Industrie Lourde :</strong> Positionnement comme expert digital dans ce secteur</li>
                <li><strong>Intégration de l'IA :</strong> Utilisation de l'intelligence artificielle pour l'automatisation du marketing</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                PME industrielles, entreprises de taille intermédiaire dans le secteur manufacturier et opérateurs de l'industrie lourde.</p>
                """,
                'excerpt': 'Intégrateur ERP spécialisé dans l\'industrie manufacturière, expert en planification de production et solutions Cegid Manufacturing PMI et Open-Prod.',
                'partner_solutions': ['Cegid Manufacturing PMI', 'Open-Prod', 'Mautic'],
                'site': ''
            },
            {
                'name': 'Absys Cyborg',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                Absys Cyborg est une filiale à 100% du Groupe Keyrus, un acteur majeur de la transformation numérique. L'entreprise bénéficie de plus de 35 ans d'expertise dans l'informatique de gestion. Elle compte 3 300 clients en France et à l'international, emploie 560 collaborateurs et a réalisé un chiffre d'affaires de 86 millions d'euros en 2023. Absys Cyborg opère à travers 13 agences en France et 2 à l'international (Bruxelles et Londres).</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Conseil en Transformation Numérique :</strong> Guide les organisations dans la refonte de leurs solutions de gestion</li>
                <li><strong>Intégration ERP, CRM, BI, Finance, RH :</strong> Expertise principale dans le déploiement et l'intégration de ces types de solutions</li>
                <li><strong>Transformation Financière :</strong> Solutions robustes en gestion de trésorerie et ERP financiers</li>
                <li><strong>Digitalisation des Processus :</strong> Numérisation des processus métier, y compris les flux entrants et sortants</li>
                <li><strong>Services Cloud :</strong> Services d'hébergement et de services gérés</li>
                <li><strong>Facturation Électronique :</strong> Solutions pour la facturation électronique en accord avec les changements réglementaires</li>
                <li><strong>Projets Internationaux :</strong> Support des initiatives mondiales grâce aux agences internationales</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Sage Platinum Partner (plus haut niveau de certification Sage)</li>
                <li>Microsoft Dynamics Gold Partner (certifié pour l'ERP et le CRM)</li>
                <li>Intégrateur et Revendeur Certifié Kyriba</li>
                <li>SMB Competence Center et Mid Market Competence Center</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                PME et ETI de tous secteurs d'activité, avec une expertise particulière pour les professionnels de la comptabilité et les cabinets cherchant des solutions comptables avancées et intégrées.</p>
                """,
                'excerpt': 'Filiale du Groupe Keyrus, expert en transformation numérique avec 35 ans d\'expérience. Sage Platinum Partner et Microsoft Gold Partner.',
                'partner_solutions': ['Sage X3', 'Sage FRP 1000', 'Sage 100', 'Sage Fiscalité', 'Microsoft Dynamics 365', 'Power Platform', 'Kyriba', 'Lucca', 'Silae', 'MyReport', 'Pennylane'],
                'site': ''
            },
            {
                'name': 'Apogea',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                Apogea est un intégrateur leader avec plus de 30 ans d'expérience, faisant partie du Groupe Proxiteam. L'entreprise emploie plus de 360 collaborateurs, dont 150 consultants certifiés. Apogea sert plus de 4 000 clients entreprises et opère à travers 15 agences, assurant une proximité locale.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Intégration ERP :</strong> Maximisation de l'efficacité des entreprises avec des solutions ERP couvrant facturation/devis, gestion commerciale, achats, finance, production, chaîne d'approvisionnement et gestion de projets</li>
                <li><strong>SIRH :</strong> Optimisation et simplification de la gestion du capital humain, incluant la paie, gestion des temps, des congés, des talents, la GPEC et les notes de frais</li>
                <li><strong>Gestion Financière :</strong> Optimisation de la comptabilité, contrôle des dépenses et maximisation de la rentabilité, incluant fiscalité, immobilisations, trésorerie, facturation électronique, recouvrement de créances et rapprochement bancaire</li>
                <li><strong>BI (Business Intelligence) :</strong> Indicateurs de performance, reporting et tableaux de bord</li>
                <li><strong>CRM :</strong> Développement de stratégies centrées sur le client, avec des CRM spécialisés pour diverses industries</li>
                <li><strong>Opérateur de Transformation Digitale :</strong> Positionnement comme opérateur de transformation digitale pour toutes les fonctions métier</li>
                <li><strong>Formation :</strong> Certifiée Qualiopi pour des programmes de formation personnalisables</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Certifié Qualiopi pour la qualité des formations</li>
                <li>150 consultants certifiés</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                TPE/PME, ETI et Collectivités en France. Solutions CRM adaptées aux experts-comptables avec des solutions financières complètes très pertinentes pour les cabinets d'expertise comptable.</p>
                """,
                'excerpt': 'Intégrateur leader avec 30+ ans d\'expérience, 4000+ clients, expert en ERP, SIRH et solutions financières. Certifié Qualiopi.',
                'partner_solutions': ['Sage Business Cloud Paie', 'Sage Paie et RH', 'Sage 100', 'Sage 1000', 'Sage Intacct', 'Sage Business Cloud Comptabilité', 'Sage Fiscalité', 'Sage BI Reportings', 'Sage CRM', 'Cegid Talentsoft', 'Cegid HR Ultimate', 'Microsoft Business Central', 'Microsoft Dynamics 365', 'Power BI', 'Lucca', 'MyReport', 'Silae', 'Yooz', 'Pennylane', 'Clearnox', 'EBP', 'ZeenDoc', 'Agicap'],
                'site': ''
            },
            {
                'name': 'BDO France – Software & Services',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                BDO France – Software & Services est une entité du réseau d'audit BDO avec plus de 30 ans d'expérience dans la mise en œuvre et l'exploitation de solutions informatiques. Sa mission est de proposer des solutions fiables en adéquation avec les besoins et les objectifs de ses clients.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Intégration ERP :</strong> Centralisation des données et gestion en temps réel des fonctions pour divers secteurs d'activité</li>
                <li><strong>Gestion Financière et Comptable :</strong> Expertise en logiciels de comptabilité, trésorerie, paie et RH</li>
                <li><strong>Gestion Commerciale :</strong> Pilotage des ventes, CRM, SAV, stocks, achats</li>
                <li><strong>Gestion de Production :</strong> Solutions spécialisées Sage 100 Industrie pour les PMI, optimisant les chaînes de production et le suivi des performances</li>
                <li><strong>Transformation Digitale :</strong> Positionnement au cœur de la transformation numérique des entreprises</li>
                <li><strong>Dématérialisation :</strong> Solutions pour la dématérialisation des factures clients et fournisseurs</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Certifié QUALIOPI pour la formation professionnelle continue</li>
                <li>Bénéficie des certifications ISO du réseau BDO en matière de sécurité de l'information et de gestion de la qualité</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                TPE, PME, PMI et ETI, avec une concentration spécifique sur les entreprises industrielles de taille moyenne. Très pertinent pour les professionnels de la comptabilité grâce à l'orientation Sage 100 et Pennylane.</p>
                """,
                'excerpt': 'Entité du réseau BDO avec 30+ ans d\'expérience, spécialisée en Sage 100 et Everwin pour PME/PMI. Certifié Qualiopi.',
                'partner_solutions': ['Sage 100', 'Everwin', 'Pennylane'],
                'site': ''
            },
            {
                'name': 'Bworkshop',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                Bworkshop est une agence spécialisée dans le conseil et l'intégration de solutions ERP. L'entreprise se consacre à l'intégration des systèmes d'information et à leur transformation digitale, en mettant l'accent sur l'optimisation du back-office d'une entreprise pour améliorer sa compétitivité. Elle dispose d'une équipe de collaborateurs qualifiés et opère pour ses clients dans plusieurs pays, employant entre 50 et 99 salariés en 2022.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Intégration ERP Back-Office :</strong> Objectif principal d'intégration des systèmes d'information pour les opérations de back-office</li>
                <li><strong>Expertise Oracle ERP :</strong> Spécialisation approfondie dans JD Edwards et NetSuite</li>
                <li><strong>Transformation Digitale :</strong> Accompagnement des clients dans leur parcours de transformation numérique</li>
                <li><strong>Digitalisation P2P (Procure-to-Pay) et O2C (Order-to-Cash) :</strong> Automatisation de ces cycles pour améliorer l'efficacité, la visibilité et réduire les coûts</li>
                <li><strong>Gestion de Trésorerie :</strong> Transformation de la liquidité en un vecteur dynamique de croissance</li>
                <li><strong>Oracle Cloud Infrastructure (OCI) :</strong> Expertise en migration et optimisation cloud</li>
                <li><strong>TMA (Tierce Maintenance Applicative) :</strong> Support et amélioration continue pour les systèmes ERP</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Certifications NetSuite : SuiteFoundation, ERP Consultant et Administrator</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                Entreprises de toutes tailles, avec une mention particulière pour les PME et ETI concernant les solutions de gestion de trésorerie. L'inclusion de solutions de gestion de trésorerie et de numérisation P2P est très pertinente pour les PME/ETI et les experts-comptables.</p>
                """,
                'excerpt': 'Agence spécialisée en ERP Oracle (JD Edwards, NetSuite) et transformation digitale. Expert en back-office et gestion de trésorerie.',
                'partner_solutions': ['Oracle JD Edwards', 'NetSuite', 'Kyriba', 'Esker', 'Agicap', 'Jedox', 'Oracle Cloud Infrastructure'],
                'site': ''
            },
            {
                'name': 'CIAG',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                CIAG est une ESN (Entreprise de Services du Numérique) basée à Toulouse et opérant dans la région du Grand Sud-Ouest de la France. L'entreprise est un partenaire expert depuis 1982, bénéficiant de plus de 40 ans d'expérience. Elle a mené à bien plus de 400 projets pour ses clients.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Intégration ERP :</strong> Expertise en Divalto et Infor, couvrant un large éventail de domaines fonctionnels</li>
                <li><strong>Gestion Financière :</strong> Spécialisation approfondie dans Infor Anael Finance, incluant la comptabilité, la trésorerie, la conformité et la numérisation des processus pour les départements financiers</li>
                <li><strong>RH et Paie :</strong> Solutions pour les Ressources Humaines et la Gestion des Temps et des Activités (GTA)</li>
                <li><strong>Développement Personnalisé :</strong> Fortes capacités en Java, Talend, AS/400 et Node</li>
                <li><strong>Environnements IBM :</strong> Compétence solide sur les systèmes IBM AS400 – Power i</li>
                <li><strong>Haute Disponibilité :</strong> Certifié pour les solutions Quick-EDD HA</li>
                <li><strong>Facturation Électronique :</strong> Accompagnement sur la dématérialisation des factures</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Certifié Qualiopi (renouvelée le 7 juillet 2024)</li>
                <li>Partenaire IBM et Certifié IBM sur les serveurs IBM Power i</li>
                <li>Certifié TRADER'S (groupe Syncsort) pour les solutions de haute disponibilité Quick-EDD</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                Entreprises de Toulouse et de la région du Grand Sud-Ouest, TPE-PME et professionnels de la finance (DAF, contrôleurs de gestion, comptables, trésoriers). Très pertinent pour les experts-comptables grâce à l'expertise en "Comptabilité-Finance" et Infor Anael Finance.</p>
                """,
                'excerpt': 'ESN toulousaine avec 40+ ans d\'expérience, spécialisée en Divalto et Infor Anael Finance. Expert comptabilité-finance et IBM.',
                'partner_solutions': ['Divalto Infinity', 'Divalto Weavy', 'Infor Anael Finance', 'Infor Anael RH', 'Infor Anael Travail Temporaire', 'Asys', 'LD Système', 'IBM Power i', 'Talend'],
                'site': ''
            },
            {
                'name': 'Captivea',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                Captivea est un intégrateur ERP et consultant en affaires de portée mondiale, leader mondial de l'intégration Odoo. L'entreprise est présente sur quatre continents : Amérique du Nord, Europe, Asie et Afrique. Captivea possède plus de 16 ans d'expérience dans l'intégration et l'implémentation de systèmes ERP, avec une méthodologie de projet approuvée par plus de 600 clients satisfaits.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Intégration Odoo et Cegid ERP :</strong> Expertise principale dans le déploiement, la personnalisation et le développement de ces deux plateformes ERP</li>
                <li><strong>Open Source et Cloud :</strong> Spécialisation dans les solutions open source (Odoo) et les déploiements cloud (Odoo Cloud, Cegid XRP Flex SaaS)</li>
                <li><strong>Conseil en Affaires :</strong> Services de conseil pour améliorer les processus internes et rationaliser les opérations commerciales</li>
                <li><strong>Intégration par Industrie :</strong> Solutions ERP spécialisées pour diverses industries, notamment la finance, l'assurance, l'imprimerie, la logistique, la fabrication et l'aérospatiale</li>
                <li><strong>Automatisation Fiscale :</strong> Grâce à l'intégration d'Avalara avec Odoo, automatisation du calcul et de la gestion des taxes</li>
                <li><strong>Méthodologie Agile :</strong> Approche agile pour un déploiement progressif et adaptable des solutions</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Odoo Gold Partner Certifié (plus haut niveau de partenariat Odoo)</li>
                <li>Partenaire Certifié pour les versions Odoo 12 à 18</li>
                <li>Certifié ISO 27001 pour les données hébergées Cegid XRP Flex</li>
                <li>Plusieurs nominations et récompenses, dont "Meilleur Partenaire en Europe et Amérique du Nord pour 2024"</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                Organisations de toutes tailles, des petites entreprises aux grandes organisations, avec une mention spécifique pour les petites et moyennes entreprises. Offre des solutions ERP Odoo spécifiquement pour le secteur financier et le secteur des assurances.</p>
                """,
                'excerpt': 'Leader mondial de l\'intégration Odoo avec 16+ ans d\'expérience. Odoo Gold Partner présent sur 4 continents.',
                'partner_solutions': ['Odoo ERP', 'Cegid XRP Flex', 'Avalara', 'Agicap', 'YOOZ'],
                'site': ''
            },
            {
                'name': 'Groupe SRA',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                Le Groupe SRA est un intégrateur de logiciels avec plus de 40 ans d'expérience, reconnu comme le premier partenaire Sage en France. L'entreprise a une portée nationale et internationale, avec de nombreuses agences en France (Angoulême, Avignon, Bordeaux, Clermont-Ferrand, Lorient, Lyon, Nice, Paris, Rennes, Toulouse) et à l'étranger (Afrique, Guadeloupe, Martinique, Réunion, Tunisie, Madagascar). Le Groupe SRA est en constante évolution, ayant renforcé son expertise en infrastructure informatique et en intégration CRM avec des acquisitions récentes.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Expertise Sage :</strong> Position de "Premier partenaire Sage en France" indiquant une maîtrise totale de la gamme Sage, avec des équipes certifiées par l'éditeur</li>
                <li><strong>Gestion Financière & Comptable :</strong> Offres complètes pour la gestion comptable et financière</li>
                <li><strong>Gestion de la Paie et SIRH :</strong> Solutions pour la paie et les ressources humaines</li>
                <li><strong>BI et Apps Métiers :</strong> Développement d'offres en Business Intelligence et d'applications métier</li>
                <li><strong>Dématérialisation & GED :</strong> Solutions pour la dématérialisation et la gestion électronique de documents</li>
                <li><strong>Conseil et Intégration :</strong> Accompagnement des PME et ETI dans leurs projets informatiques</li>
                <li><strong>Diversité Sectorielle :</strong> Expertise couvrant de nombreux secteurs (agroalimentaire, associations, BTP, vignobles, commerce, industrie, services, transport, logistique, santé)</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Certifié Qualiopi pour la qualité des activités de formation</li>
                <li>Premier partenaire Sage 2023</li>
                <li>Consultants certifiés par leurs éditeurs</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                PME régionales et groupes internationaux. La profondeur de leur offre Sage, incluant la fiscalité et la gestion financière, ainsi que l'intégration de Pennylane et Agicap, les rend particulièrement pertinents pour les experts-comptables et leurs clients PME/ETI.</p>
                """,
                'excerpt': 'Premier partenaire Sage en France avec 40+ ans d\'expérience. Présence nationale et internationale, expert en gestion financière.',
                'partner_solutions': ['Sage X3', 'Sage FRP 1000', 'Sage Intacct', 'Sage 100', 'Sage BI Reporting', 'Sage Eloficash', 'Sage Youdoc', 'Sage Fiscalité', 'Microsoft Power BI', 'Cegid Payroll Ultimate', 'Cegid XRP Flex', 'Silae', 'Lucca SIRH', 'Pennylane', 'Agicap', 'MyReport', 'HubSpot'],
                'site': ''
            },
            {
                'name': 'Koesio Data Solutions',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                Koesio Data Solutions est une ESN faisant partie du groupe Koesio télécom. L'entreprise possède plus de 20 ans d'expertise en gestion et données et 33 ans d'expérience dans le traitement de l'information documentaire ou numérique. Elle compte plus de 100 000 clients, incluant des micro-entreprises, des PME, de grandes entreprises et des collectivités locales. Koesio Data Solutions dispose de plus de 100 agences en France, en Belgique, au Luxembourg et à Monaco, avec plus de 1 500 experts numériques.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Gestion d'Entreprise et ERP :</strong> Optimisation de la productivité, de la finance, de la comptabilité, de la gestion commerciale, de la production et du bâtiment</li>
                <li><strong>Données et BI :</strong> Analyse et clarté de la vision de l'entreprise grâce aux outils d'aide à la décision Microsoft BI</li>
                <li><strong>CRM :</strong> Stratégies centrées sur le client pour la prospection et la fidélisation</li>
                <li><strong>SIRH :</strong> Digitalisation des processus RH avec Lucca et Silae</li>
                <li><strong>Développement et Connecteurs :</strong> Capacité à développer des compléments personnalisés et des connecteurs pour les solutions Sage, Salesforce et ERP</li>
                <li><strong>Gestion de Production :</strong> Expertise reconnue, accompagnant une trentaine de clients sur cette solution</li>
                <li><strong>Facturation Électronique :</strong> Accompagnement à la mise en conformité avec les solutions Sage</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Centre de Compétence Sage | Partenaire Platinum (plus haut niveau de partenariat avec Sage)</li>
                <li>Microsoft Gold Data Analytics et Power BI</li>
                <li>Partenaire Certifié Salesforce</li>
                <li>Partenaire Certifié Lucca</li>
                <li>Plus d'une centaine de certifications informatiques et logicielles</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                Micro-entreprises, PME, ETI, grandes entreprises et collectivités publiques. Positionnement comme partenaire numéro un pour les PME et les collectivités locales pour leurs projets numériques.</p>
                """,
                'excerpt': 'Grande ESN du groupe Koesio avec 100+ agences, 100 000+ clients. Sage Platinum Partner et Microsoft Gold Data Analytics.',
                'partner_solutions': ['Sage 100', 'Sage FRP 1000', 'Sage SDMO', 'Sage Batigest', 'Sage Paie', 'Sage GPAO', 'Microsoft Power BI', 'Azure Data Factory', 'Salesforce', 'Silae', 'Lucca', 'Avanteam'],
                'site': ''
            },
            {
                'name': 'Mercuria',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                Mercuria est un distributeur et intégrateur de logiciels de gestion, présent sur la moitié nord de la France avec des implantations à Nantes, Paris, Rouen et Strasbourg. L'entreprise a plus de 20 ans d'expérience dans le domaine et se spécialise dans la comptabilité, la finance et les RH.</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Comptabilité & Immobilisations :</strong> Aide à la recherche de la solution de gestion comptable idéale</li>
                <li><strong>Paie & SIRH :</strong> Logiciels dédiés à la paie et aux ressources humaines</li>
                <li><strong>Trésorerie & Recouvrement :</strong> Pilotage de la performance financière et maîtrise du recouvrement</li>
                <li><strong>Dématérialisation, Réforme & GED :</strong> Gestion des factures avec une dématérialisation efficace et conformité à la réforme de la facturation électronique</li>
                <li><strong>Reporting & Fiscalité :</strong> Automatisation du reporting et gain d'efficacité dans la chaîne fiscale</li>
                <li><strong>Conseil et Intégration :</strong> Accompagnement des clients dans le choix et la mise en œuvre de solutions logicielles</li>
                <li><strong>Formation :</strong> Programmes de formation sur leurs logiciels, assurant une adoption rapide et efficace</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Certifié Qualiopi pour les programmes de formation</li>
                <li>Revendeur Sage Certifié avec tous les commerciaux et consultants certifiés selon un cursus contrôlé par l'éditeur</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                PME et ETI. Leur expertise historique en Sage, combinée à des solutions de dématérialisation, de fiscalité et de gestion de trésorerie, les rend particulièrement pertinents pour les experts-comptables et les PME soucieuses de leur conformité.</p>
                """,
                'excerpt': 'Distributeur Sage certifié avec 20+ ans d\'expérience, spécialisé comptabilité/finance. Présent dans le nord de la France.',
                'partner_solutions': ['Sage FRP 1000', 'Sage 100', 'Sage XRT', 'Sage Intacct', 'Lucca', 'Elo Digital Office', 'Regnology Uloa', 'Avista eXFiles', 'Yooz', 'Mata Io'],
                'site': ''
            },
            {
                'name': 'TGS France',
                'description': """
                <p><strong>Profil de l'Entreprise :</strong><br>
                TGS France est un intégrateur historique de Divalto, reconnu parmi les 10 premiers intégrateurs Divalto en France. Le pôle informatique de TGS France possède plus de 10 ans d'expérience dans l'intégration de l'ERP Divalto. L'entreprise fait partie du groupe TGS France, qui offre une gamme plus large de services (comptabilité, audit, conseil, RH, etc.).</p>

                <p><strong>Spécialisations Principales :</strong></p>
                <ul>
                <li><strong>Intégration ERP Divalto :</strong> Expertise historique et approfondie dans Divalto Infinity, avec une capacité à gérer des projets complexes et de grande envergure</li>
                <li><strong>Spécialisations Sectorielles :</strong> Grâce à des investissements conjoints avec Divalto, spécialisation dans le négoce, le service et l'industrie. Solutions spécifiques pour les industries du bois et du verre, ainsi que pour le secteur du commerce de détail</li>
                <li><strong>Gestion Commerciale, CRM, Production, Finance, RH :</strong> Divalto Infinity couvre toutes ces fonctions clés</li>
                <li><strong>Développement Personnalisé :</strong> Capacité à concevoir des solutions métier sur mesure en complément des modules existants</li>
                <li><strong>Dématérialisation des Factures :</strong> Expertise dans la dématérialisation des factures clients sur l'ERP Divalto</li>
                </ul>

                <p><strong>Certifications :</strong></p>
                <ul>
                <li>Divalto Platinum Partner et High End Partner (plus haut niveau de certification de Divalto)</li>
                <li>Certifié ScoreFact pour la qualité de sa relation client</li>
                <li>Reconnu parmi les "meilleurs cabinets d'expertise comptable 2025" par Le Point (pour le groupe TGS France)</li>
                </ul>

                <p><strong>Public Cible :</strong><br>
                Entreprises industrielles, du négoce et du retail. Plus largement, le groupe TGS France sert entrepreneurs et professionnels, PME et ETI, associations et entités publiques, et propriétaires immobiliers. La mention de la "profession comptable" comme spécialisation indique une compréhension des besoins des experts-comptables.</p>
                """,
                'excerpt': 'Top 10 intégrateur Divalto en France avec 10+ ans d\'expérience. Divalto Platinum Partner, expert en industrie et négoce.',
                'partner_solutions': ['Divalto Infinity', 'Divalto Weavy', 'Générix', 'Divalto Miroiterie et Marbrerie'],
                'site': ''
            }
        ]

        self.stdout.write(self.style.SUCCESS('Début de l\'importation des intégrateurs...'))

        for integrator_data in integrators_data:
            # Create or update integrator
            integrator, created = Integrator.objects.get_or_create(
                slug=slugify(integrator_data['name']),
                defaults={
                    'name': integrator_data['name'],
                    'description': integrator_data['description'],
                    'excerpt': integrator_data['excerpt'],
                    'site': integrator_data['site'],
                    'is_published': True
                }
            )

            if not created:
                # Update existing integrator
                integrator.description = integrator_data['description']
                integrator.excerpt = integrator_data['excerpt']
                integrator.save()

            # Link software solutions
            for solution_name in integrator_data['partner_solutions']:
                # Try to find matching software by name (case insensitive)
                software_matches = Software.objects.filter(name__icontains=solution_name)
                
                if software_matches.exists():
                    for software in software_matches:
                        integrator.softwares.add(software)
                        self.stdout.write(f'  ✓ Lié {integrator.name} à {software.name}')
                else:
                    # Try partial matches for complex names
                    partial_matches = []
                    for word in solution_name.split():
                        if len(word) > 3:  # Only search for words longer than 3 characters
                            matches = Software.objects.filter(name__icontains=word)
                            partial_matches.extend(matches)
                    
                    if partial_matches:
                        # Remove duplicates
                        unique_matches = list(set(partial_matches))
                        for software in unique_matches:
                            integrator.softwares.add(software)
                            self.stdout.write(f'  ✓ Lié {integrator.name} à {software.name} (correspondance partielle)')
                    else:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Aucun logiciel trouvé pour "{solution_name}" (intégrateur: {integrator.name})'))

            action = 'Créé' if created else 'Mis à jour'
            self.stdout.write(self.style.SUCCESS(f'{action}: {integrator.name}'))

        self.stdout.write(self.style.SUCCESS('Importation terminée avec succès!')) 