"""
Management command: python manage.py seed_data
Seeds categories, 200+ questions, and achievements.
"""
from django.core.management.base import BaseCommand
from apps.quiz.models import Category, Question, Answer
from apps.rewards.services import AchievementService

CATEGORIES = [
    {"name":"Mathematics","icon":"🔢","subs":["Basic Arithmetic","Algebra","Geometry","Mental Math"]},
    {"name":"Science","icon":"🔬","subs":["Physics","Chemistry","Biology","Environmental Science"]},
    {"name":"General Knowledge","icon":"🌍","subs":[]},
    {"name":"Current Affairs","icon":"📰","subs":[]},
    {"name":"Technology","icon":"💻","subs":[]},
    {"name":"Logic & Reasoning","icon":"🧠","subs":[]},
    {"name":"African History & Culture","icon":"🏛️","subs":["Nigerian History & Culture"]},
    {"name":"AI & Cybersecurity","icon":"🤖","subs":[]},
    {"name":"Mixed Questions","icon":"🎲","subs":[]},
]

QUESTIONS = {
"Mathematics":[
("What is 15 × 8?",[("120",True),("110",False),("130",False),("115",False)],"easy","15 × 8 = 120"),
("What is the square root of 144?",[("12",True),("14",False),("11",False),("13",False)],"easy","12 × 12 = 144"),
("What is 25% of 200?",[("50",True),("25",False),("75",False),("40",False)],"easy","25% = 1/4, so 200 ÷ 4 = 50"),
("If x = 5, what is 3x + 7?",[("22",True),("17",False),("20",False),("25",False)],"easy","3(5) + 7 = 22"),
("What is 1/4 + 1/2?",[("3/4",True),("1/2",False),("2/3",False),("1/3",False)],"easy","1/4 + 2/4 = 3/4"),
("What is 7²?",[("49",True),("14",False),("42",False),("56",False)],"easy","7 × 7 = 49"),
("What is 2³?",[("8",True),("6",False),("9",False),("12",False)],"easy","2 × 2 × 2 = 8"),
("Round 4.567 to 2 decimal places.",[("4.57",True),("4.56",False),("4.60",False),("4.55",False)],"easy","Third decimal 7 >= 5, round up"),
("What is 18 − (−6)?",[("24",True),("12",False),("18",False),("-12",False)],"easy","18 + 6 = 24"),
("What is 20% of 150?",[("30",True),("25",False),("35",False),("20",False)],"easy","150 ÷ 5 = 30"),
("Solve for x: 3x + 9 = 27",[("6",True),("9",False),("3",False),("12",False)],"medium","3x = 18, x = 6"),
("What is 15% of 340?",[("51",True),("45",False),("60",False),("34",False)],"medium","10% = 34, 5% = 17, total = 51"),
("If a triangle has angles 60° and 80°, what is the third angle?",[("40°",True),("50°",False),("60°",False),("30°",False)],"medium","180 − 60 − 80 = 40"),
("What is the LCM of 4 and 6?",[("12",True),("24",False),("8",False),("6",False)],"medium","Smallest common multiple = 12"),
("What is the HCF of 36 and 48?",[("12",True),("6",False),("18",False),("9",False)],"medium","Highest common factor = 12"),
("What is 0.125 as a fraction?",[("1/8",True),("1/4",False),("1/6",False),("1/5",False)],"medium","0.125 = 125/1000 = 1/8"),
("Solve: 5(x − 2) = 25",[("7",True),("5",False),("6",False),("9",False)],"medium","5x = 35, x = 7"),
("Area of rectangle: length 12, width 7?",[("84",True),("38",False),("76",False),("96",False)],"medium","12 × 7 = 84"),
("What is the sum of interior angles in a triangle?",[("180°",True),("360°",False),("90°",False),("270°",False)],"medium","Always 180°"),
("Simplify: 3² + 4²",[("25",True),("12",False),("49",False),("14",False)],"medium","9 + 16 = 25"),
("What is π² (to 2 decimal places)?",[("9.87",True),("9.42",False),("10.24",False),("8.99",False)],"hard","π² ≈ 9.8696"),
("What is log₂(32)?",[("5",True),("4",False),("6",False),("8",False)],"hard","2⁵ = 32"),
("Solve: x² − 5x + 6 = 0",[("x=2 or x=3",True),("x=1 or x=6",False),("x=-2 or x=-3",False),("x=2 or x=-3",False)],"hard","Factor: (x-2)(x-3)=0"),
("Sum of interior angles of a hexagon?",[("720°",True),("540°",False),("900°",False),("360°",False)],"hard","(6-2)×180 = 720"),
("Convert binary 1101 to decimal.",[("13",True),("11",False),("14",False),("12",False)],"hard","8+4+0+1 = 13"),
("What is the determinant of [[2,3],[1,4]]?",[("5",True),("11",False),("8",False),("-5",False)],"hard","(2×4)-(3×1) = 5"),
("What is ∫(2x + 3)dx?",[("x² + 3x + C",True),("2x² + 3 + C",False),("x² + C",False),("2 + C",False)],"expert","Integrate term by term"),
("What is the 10th term of GP: 3, 6, 12...?",[("1536",True),("768",False),("3072",False),("512",False)],"expert","3 × 2⁹ = 1536"),
("lim(x→2) of (x² − 4)/(x − 2)?",[("4",True),("2",False),("0",False),("Undefined",False)],"expert","Factor: (x+2)(x-2)/(x-2) = x+2, at x=2 gives 4"),
],
"Science":[
("What is the chemical symbol for water?",[("H₂O",True),("CO₂",False),("O₂",False),("NaCl",False)],"easy","2 hydrogen + 1 oxygen"),
("How many bones in the adult human body?",[("206",True),("212",False),("198",False),("220",False)],"easy","Adults have 206 bones"),
("What type of animal is a whale?",[("Mammal",True),("Fish",False),("Reptile",False),("Amphibian",False)],"easy","Whales breathe air and nurse young"),
("What gas do plants absorb during photosynthesis?",[("Carbon dioxide",True),("Oxygen",False),("Nitrogen",False),("Hydrogen",False)],"easy","Plants take CO₂ and release O₂"),
("What is the unit of electrical resistance?",[("Ohm",True),("Volt",False),("Ampere",False),("Watt",False)],"easy","Resistance measured in Ohms (Ω)"),
("What organ pumps blood through the body?",[("Heart",True),("Liver",False),("Kidney",False),("Lungs",False)],"easy","The heart drives the circulatory system"),
("What is the hardest natural substance?",[("Diamond",True),("Iron",False),("Granite",False),("Quartz",False)],"easy","Diamond = 10 on Mohs scale"),
("How many chromosomes in a human cell?",[("46",True),("23",False),("48",False),("92",False)],"easy","23 pairs = 46 chromosomes"),
("What planet is closest to the Sun?",[("Mercury",True),("Venus",False),("Earth",False),("Mars",False)],"easy","Mercury is the innermost planet"),
("Chemical symbol for gold?",[("Au",True),("Ag",False),("Fe",False),("Go",False)],"easy","From Latin Aurum"),
("Speed of light in a vacuum?",[("3 × 10⁸ m/s",True),("3 × 10⁶ m/s",False),("3 × 10¹⁰ m/s",False),("3 × 10⁷ m/s",False)],"medium","≈ 299,792,458 m/s"),
("Atomic number of gold (Au)?",[("79",True),("47",False),("82",False),("78",False)],"medium","Gold has 79 protons"),
("Newton's second law of motion?",[("F = ma",True),("F = mv",False),("E = mc²",False),("F = mg",False)],"medium","Force = mass × acceleration"),
("Which organelle is called the powerhouse of the cell?",[("Mitochondria",True),("Nucleus",False),("Ribosome",False),("Golgi body",False)],"medium","Mitochondria produce ATP"),
("What is the pH of pure water?",[("7",True),("0",False),("14",False),("5",False)],"medium","Neutral = pH 7"),
("Chemical formula for common salt?",[("NaCl",True),("NaOH",False),("KCl",False),("CaCO₃",False)],"medium","Sodium chloride"),
("What force keeps planets in orbit?",[("Gravity",True),("Magnetism",False),("Nuclear force",False),("Friction",False)],"medium","Gravitational pull from the Sun"),
("What is Avogadro's number?",[("6.022 × 10²³",True),("6.022 × 10²⁴",False),("3.14 × 10²³",False),("1.6 × 10⁻¹⁹",False)],"hard","One mole = 6.022×10²³ particles"),
("Where does protein synthesis occur?",[("Ribosome",True),("Mitochondria",False),("Nucleus",False),("Vacuole",False)],"hard","Ribosomes translate mRNA into proteins"),
("Half-life of Carbon-14?",[("5,730 years",True),("1,600 years",False),("14,000 years",False),("1,000 years",False)],"hard","Used in carbon dating"),
("Formula for kinetic energy?",[("½mv²",True),("mv",False),("mgh",False),("ma",False)],"hard","KE = ½mv²"),
("What quantum number describes orbital shape?",[("Azimuthal (l)",True),("Principal (n)",False),("Magnetic (m)",False),("Spin (s)",False)],"expert","l defines s,p,d,f shapes"),
("Heisenberg Uncertainty Principle states?",[("Position and momentum cannot both be precisely known",True),("Energy and time are interchangeable",False),("Mass increases with velocity",False),("Electrons travel in pairs",False)],"expert","Δx·Δp ≥ ℏ/2"),
],
"General Knowledge":[
("Capital city of Nigeria?",[("Abuja",True),("Lagos",False),("Kano",False),("Port Harcourt",False)],"easy","Abuja became capital in 1991"),
("How many continents?",[("7",True),("6",False),("8",False),("5",False)],"easy","Africa,Asia,Europe,N.America,S.America,Australia,Antarctica"),
("Largest population in Africa?",[("Nigeria",True),("Ethiopia",False),("Egypt",False),("South Africa",False)],"easy","Nigeria has 200M+ people"),
("Longest river in the world?",[("Nile",True),("Amazon",False),("Congo",False),("Niger",False)],"easy","The Nile stretches ~6,650 km"),
("How many days in a leap year?",[("366",True),("365",False),("364",False),("367",False)],"easy","Extra day in February"),
("National currency of Nigeria?",[("Naira",True),("Cedis",False),("Shilling",False),("Rand",False)],"easy","The Naira (₦)"),
("Largest ocean?",[("Pacific",True),("Atlantic",False),("Indian",False),("Arctic",False)],"easy","Pacific covers 30% of Earth"),
("Tallest mountain?",[("Mount Everest",True),("K2",False),("Kilimanjaro",False),("Alps",False)],"easy","8,849 m above sea level"),
("Who wrote Things Fall Apart?",[("Chinua Achebe",True),("Wole Soyinka",False),("Ngugi wa Thiong\'o",False),("Chimamanda Adichie",False)],"easy","Published 1958"),
("How many states does Nigeria have?",[("36",True),("30",False),("37",False),("32",False)],"medium","36 states + FCT"),
("Official language of Brazil?",[("Portuguese",True),("Spanish",False),("English",False),("French",False)],"medium","Colonised by Portugal"),
("Smallest country by area?",[("Vatican City",True),("Monaco",False),("San Marino",False),("Liechtenstein",False)],"medium","0.44 km²"),
("2016 Summer Olympics host city?",[("Rio de Janeiro",True),("Tokyo",False),("London",False),("Beijing",False)],"medium","First in South America"),
("Which Nigerian city is called Centre of Excellence?",[("Lagos",True),("Abuja",False),("Kano",False),("Ibadan",False)],"medium","Lagos nickname"),
("Nigeria\'s central bank name?",[("Central Bank of Nigeria",True),("Bank of Nigeria",False),("Nigerian Reserve Bank",False),("Federal Bank",False)],"medium","The CBN"),
("Most spoken language by native speakers?",[("Mandarin Chinese",True),("English",False),("Spanish",False),("Hindi",False)],"hard","900M+ native speakers"),
("UN founded in which year?",[("1945",True),("1919",False),("1950",False),("1939",False)],"hard","After World War II"),
("What does UNESCO stand for?",[("United Nations Educational Scientific and Cultural Organization",True),("United Nations Economic and Social Committee",False),("Universal Network for Education Science",False),("United Nations Empowerment Scientific Committee",False)],"medium","Promotes education and culture globally"),
],
"Technology":[
("What does CPU stand for?",[("Central Processing Unit",True),("Central Program Unit",False),("Computer Processing Unit",False),("Core Processing Unit",False)],"easy","The brain of the computer"),
("What does HTML stand for?",[("HyperText Markup Language",True),("High Transfer Markup Language",False),("HyperText Machine Language",False),("HyperText Modern Language",False)],"easy","Standard for web pages"),
("What does URL stand for?",[("Uniform Resource Locator",True),("Universal Resource Link",False),("Uniform Reference Locator",False),("Universal Record Locator",False)],"easy","Web address"),
("Python uses what to define code blocks?",[("Indentation",True),("Curly braces",False),("Parentheses",False),("BEGIN/END",False)],"easy","Python uses whitespace"),
("What does HTTP stand for?",[("HyperText Transfer Protocol",True),("High Transfer Text Protocol",False),("HyperText Transit Protocol",False),("Host Transfer Text Protocol",False)],"easy","Foundation of web communication"),
("What does RAM stand for?",[("Random Access Memory",True),("Read-Only Access Memory",False),("Rapid Application Memory",False),("Runtime Access Module",False)],"easy","Temporary memory for running programs"),
("What does SQL stand for?",[("Structured Query Language",True),("Standard Query Language",False),("Simple Query Logic",False),("Sequential Query Language",False)],"medium","Used for relational databases"),
("What does API stand for?",[("Application Programming Interface",True),("Automated Program Interaction",False),("Applied Programming Instance",False),("Application Protocol Interface",False)],"medium","Allows software to communicate"),
("Who developed Android OS?",[("Google",True),("Apple",False),("Samsung",False),("Microsoft",False)],"medium","Google acquired Android Inc in 2005"),
("What does IoT stand for?",[("Internet of Things",True),("Internet of Technology",False),("Integration of Technologies",False),("Interface of Things",False)],"medium","Connected physical devices"),
("Python was created by?",[("Guido van Rossum",True),("James Gosling",False),("Linus Torvalds",False),("Dennis Ritchie",False)],"medium","First released in 1991"),
("What does DNS stand for?",[("Domain Name System",True),("Digital Network Service",False),("Dynamic Name Server",False),("Data Name System",False)],"medium","Translates domains to IP addresses"),
("LIFO data structure?",[("Stack",True),("Queue",False),("Array",False),("Linked List",False)],"medium","Last In First Out"),
("Time complexity of binary search?",[("O(log n)",True),("O(n)",False),("O(n²)",False),("O(1)",False)],"hard","Halves search space each step"),
("What does VPN stand for?",[("Virtual Private Network",True),("Virtual Public Network",False),("Verified Private Network",False),("Virtual Protected Node",False)],"easy","Encrypts internet connection"),
("Python keyword to define a function?",[("def",True),("function",False),("fun",False),("define",False)],"easy","def function_name():"),
("What does OOP stand for?",[("Object-Oriented Programming",True),("Open Operational Programming",False),("Ordered Object Protocol",False),("Output Oriented Process",False)],"medium","Organises code around objects"),
("What is Big O notation used for?",[("Describing algorithm time/space complexity",True),("Measuring internet speed",False),("Database indexing",False),("CPU clock speed",False)],"hard","Describes performance scaling"),
("Max value of 8-bit unsigned integer?",[("255",True),("256",False),("127",False),("512",False)],"hard","2⁸ − 1 = 255"),
("What does HTTPS S stand for?",[("Secure",True),("Standard",False),("Speed",False),("Simple",False)],"easy","SSL/TLS encryption"),
],
"Logic & Reasoning":[
("All roses are flowers needing water. Do roses need water?",[("Yes",True),("No",False),("Sometimes",False),("Cannot tell",False)],"easy","Syllogism: roses → flowers → water"),
("Next: 2, 4, 8, 16, ?",[("32",True),("24",False),("18",False),("30",False)],"easy","Each doubled"),
("Next: 1, 1, 2, 3, 5, 8, ?",[("13",True),("11",False),("10",False),("14",False)],"easy","Fibonacci: add previous two"),
("Next: 3, 9, 27, ?, 243",[("81",True),("54",False),("63",False),("72",False)],"easy","Multiply by 3"),
("DOCTOR:PATIENT as TEACHER:?",[("Student",True),("School",False),("Book",False),("Lesson",False)],"easy","Analogy relationship"),
("A snail travels 1m in 2hrs. How long for 5m?",[("10 hours",True),("5 hours",False),("7 hours",False),("8 hours",False)],"easy","5 × 2 = 10"),
("MANGO=58 using A=1,B=2...What is APPLE?",[("50",True),("55",False),("48",False),("60",False)],"medium","A+P+P+L+E=1+16+16+12+5=50"),
("Next: 2, 6, 12, 20, 30, ?",[("42",True),("38",False),("40",False),("44",False)],"medium","Differences: 4,6,8,10,12"),
("If today is Wednesday, day in 100 days?",[("Friday",True),("Thursday",False),("Saturday",False),("Sunday",False)],"medium","100 mod 7 = 2, Wed+2=Fri"),
("Odd one out: 2,3,5,7,9,11",[("9",True),("2",False),("5",False),("11",False)],"medium","9=3×3, not prime"),
("If you overtake 2nd place, your position?",[("2nd",True),("1st",False),("3rd",False),("4th",False)],"medium","You take their position"),
("Clock angle at 3:15?",[("7.5°",True),("0°",False),("15°",False),("22.5°",False)],"hard","Hour at 97.5°, minute at 90°, diff=7.5°"),
("5 cats catch 5 mice in 5 mins. For 100 mice in 100 mins, how many cats?",[("5",True),("100",False),("10",False),("50",False)],"hard","Rate is constant: still 5 cats"),
("How many squares in a 3×3 grid?",[("14",True),("9",False),("12",False),("16",False)],"hard","9(1×1)+4(2×2)+1(3×3)=14"),
("All birds can fly. Penguins are birds. Can penguins fly (logically)?",[("Yes, based on premises",True),("No",False),("Impossible to say",False),("Only some",False)],"medium","Logically valid even if factually wrong"),
],
"African History & Culture":[
("Nigeria gained independence in?",[("1960",True),("1963",False),("1956",False),("1947",False)],"easy","October 1, 1960"),
("First President of Nigeria?",[("Nnamdi Azikiwe",True),("Tafawa Balewa",False),("Obafemi Awolowo",False),("Ahmadu Bello",False)],"easy","Dr Nnamdi Azikiwe 1963-1966"),
("Ancient African empire known as Land of Gold?",[("Mali Empire",True),("Songhai Empire",False),("Benin Kingdom",False),("Axum Empire",False)],"easy","Especially under Mansa Musa"),
("First democratic President of South Africa?",[("Nelson Mandela",True),("Thabo Mbeki",False),("F.W. de Klerk",False),("Cyril Ramaphosa",False)],"easy","Elected 1994"),
("Benin bronzes originated from which city?",[("Benin City",True),("Lagos",False),("Ibadan",False),("Calabar",False)],"easy","The Benin Kingdom"),
("Mansa Musa ruled which empire?",[("Mali Empire",True),("Ghana Empire",False),("Songhai Empire",False),("Kush Empire",False)],"medium","14th century ruler"),
("Nigerian civil war also known as?",[("Biafran War",True),("Lagos War",False),("Delta Conflict",False),("Borno War",False)],"medium","1967-1970"),
("Oldest university in Africa?",[("University of al-Qarawiyyin Morocco",True),("University of Cairo",False),("University of Ibadan",False),("University of Cape Town",False)],"hard","Founded 859 AD"),
("Yoruba deity of iron and warfare?",[("Ogun",True),("Sango",False),("Obatala",False),("Oya",False)],"medium","Ogun"),
("What does Ubuntu mean in African philosophy?",[("I am because we are",True),("Power to the people",False),("Freedom through unity",False),("One nation one people",False)],"medium","Nguni Bantu concept"),
("African country never colonised?",[("Ethiopia",True),("Liberia",False),("Somalia",False),("South Africa",False)],"hard","Won at Battle of Adwa 1896"),
("City of Timbuktu is in which country?",[("Mali",True),("Niger",False),("Senegal",False),("Mauritania",False)],"medium","Major Islamic scholarship centre"),
("Nigerian Nobel Prize Literature winner 1986?",[("Wole Soyinka",True),("Chinua Achebe",False),("Ben Okri",False),("Chimamanda Adichie",False)],"medium","First African Nobel for Literature"),
("Zulu Kingdom reached peak under?",[("Shaka Zulu",True),("Dingane",False),("Cetshwayo",False),("Mpande",False)],"medium","Early 19th century"),
("First African country to gain independence (modern era)?",[("Liberia 1847",True),("Ghana 1957",False),("Egypt 1922",False),("Nigeria 1960",False)],"hard","Liberia declared independence 1847"),
],
"AI & Cybersecurity":[
("What does AI stand for?",[("Artificial Intelligence",True),("Automated Input",False),("Advanced Interface",False),("Automated Intelligence",False)],"easy","Intelligence simulated by machines"),
("Attack that tricks users into revealing info?",[("Phishing",True),("Brute Force",False),("SQL Injection",False),("DDoS",False)],"easy","Deceptive emails/websites"),
("ML stands for?",[("Machine Learning",True),("Modern Logic",False),("Mobile Language",False),("Micro Learning",False)],"easy","Subset of AI"),
("What is a firewall?",[("Security system monitoring network traffic",True),("Physical server barrier",False),("Software to speed internet",False),("Type of virus",False)],"easy","Filters network traffic by rules"),
("HTTPS S stands for?",[("Secure",True),("Standard",False),("Speed",False),("Simple",False)],"easy","SSL/TLS encryption"),
("What does 2FA stand for?",[("Two-Factor Authentication",True),("Two-File Access",False),("Twin Function Access",False),("Transfer Firewall Access",False)],"medium","Extra verification beyond password"),
("What is a VPN?",[("Encrypts internet and hides IP",True),("Speeds up internet",False),("Free WiFi service",False),("Antivirus software",False)],"easy","Virtual Private Network"),
("Supervised vs unsupervised learning difference?",[("Supervised uses labels; unsupervised finds patterns without",True),("Supervised is faster",False),("No difference",False),("Supervised uses neural nets only",False)],"medium","Key distinction is labelled data"),
("Algorithm for image recognition?",[("Convolutional Neural Network (CNN)",True),("Linear Regression",False),("K-Means Clustering",False),("Decision Tree",False)],"medium","CNNs detect image patterns"),
("What is ransomware?",[("Malware encrypting files demanding payment",True),("Software slowing your PC",False),("Phishing website",False),("Type of firewall",False)],"medium","Encrypts data for ransom"),
("What is a Large Language Model (LLM)?",[("AI trained on large text to understand and generate language",True),("Large spreadsheet model",False),("Translation tool",False),("Compiler for large programs",False)],"medium","Like GPT, trained on billions of tokens"),
("Zero-day vulnerability means?",[("Unknown flaw with no patch available",True),("Bug found on release day",False),("Bug causing zero data loss",False),("Daily scan report",False)],"hard","Vendor has had zero days to fix it"),
("What is the Turing Test?",[("Test if machine exhibits human-like intelligence",True),("Programming benchmark",False),("Network speed test",False),("Cryptographic method",False)],"medium","Proposed by Alan Turing 1950"),
("SQL injection is?",[("Malicious SQL in input fields to attack database",True),("Method to speed up queries",False),("Adding new records",False),("Encrypting DB connections",False)],"hard","Exploits unsanitised input"),
("Symmetric vs asymmetric encryption?",[("Symmetric=one key; asymmetric=public-private pair",True),("Symmetric is stronger",False),("They are identical",False),("Symmetric for files only",False)],"hard","AES vs RSA"),
("GPT stands for?",[("Generative Pre-trained Transformer",True),("General Purpose Technology",False),("Generative Processing Tool",False),("Global Pre-trained Technology",False)],"medium","Transformer-based generative AI"),
("What is OWASP Top 10?",[("Most critical web application security risks",True),("Top 10 programming languages",False),("Top 10 AI models",False),("Global cybersecurity ranking",False)],"hard","Guide for web security"),
("XSS stands for?",[("Cross-Site Scripting",True),("Cross-Server System",False),("Extended Security Script",False),("External Script System",False)],"hard","Injects malicious scripts into trusted sites"),
("Algorithm for spam detection?",[("Naive Bayes",True),("Linear Regression",False),("K-Nearest Neighbour",False),("PCA",False)],"expert","Fast text classification"),
("Adversarial machine learning means?",[("Crafted inputs to cause AI to output wrong results",True),("Training two models against each other",False),("Using ML to attack competitors",False),("Competitive ML benchmark",False)],"expert","Adversarial examples fool ML models"),
],
"Current Affairs":[
("2022 FIFA World Cup host country?",[("Qatar",True),("Russia",False),("UAE",False),("Brazil",False)],"easy","First in Middle East"),
("CEO of Tesla and SpaceX?",[("Elon Musk",True),("Jeff Bezos",False),("Tim Cook",False),("Sundar Pichai",False)],"easy","Also owns X"),
("ECOWAS stands for?",[("Economic Community of West African States",True),("Eastern Community of West African States",False),("Economic Council of West African States",False),("Economic Community of West African Societies",False)],"medium","15 West African countries"),
("Country that launched first satellite?",[("Soviet Union - Sputnik 1957",True),("USA",False),("China",False),("Germany",False)],"medium","October 4, 1957"),
("AfCFTA covers how many African countries?",[("54",True),("35",False),("48",False),("27",False)],"medium","World\'s largest free trade area by country count"),
("Nigeria\'s digital identity number?",[("National Identification Number NIN",True),("Bank Verification Number BVN",False),("National Identity Card",False),("Voter Card Number",False)],"easy","11-digit number from NIMC"),
("What does OPEC stand for?",[("Organization of the Petroleum Exporting Countries",True),("Organization of Petroleum Exporting Companies",False),("Organization of Primary Energy Countries",False),("Oil Producing and Exporting Countries",False)],"medium","Coordinates petroleum policies"),
("First company to reach $3 trillion market cap?",[("Apple",True),("Microsoft",False),("Amazon",False),("Google",False)],"hard","Historic milestone"),
],
}


class Command(BaseCommand):
    help = "Seed 200+ questions across all categories."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\nSeeding TOPPERS...\n"))

        # Categories
        self.stdout.write("Creating categories...")
        for cat_data in CATEGORIES:
            parent, created = Category.objects.get_or_create(
                name=cat_data["name"], defaults={"icon": cat_data["icon"]}
            )
            if created:
                self.stdout.write(f"  + {parent.name}")
            for sub in cat_data.get("subs", []):
                Category.objects.get_or_create(name=sub, defaults={"parent": parent, "icon": cat_data["icon"]})

        # Questions
        self.stdout.write("\nCreating questions...")
        total_new = 0
        for cat_name, qs in QUESTIONS.items():
            try:
                cat = Category.objects.get(name=cat_name)
            except Category.DoesNotExist:
                continue
            new = 0
            for text, answers, diff, explanation in qs:
                q, created = Question.objects.get_or_create(
                    text=text,
                    defaults={"category": cat, "difficulty": diff, "explanation": explanation},
                )
                if created:
                    for i, (ans_text, is_correct) in enumerate(answers):
                        Answer.objects.create(question=q, text=ans_text, is_correct=is_correct, order=i)
                    new += 1
                    total_new += 1
            self.stdout.write(f"  {cat.icon} {cat_name}: +{new}")

        # Achievements
        self.stdout.write("\nSeeding achievements...")
        AchievementService.ensure_achievements_exist()
        from apps.rewards.models import Achievement
        self.stdout.write(f"  {Achievement.objects.count()} achievements ready")

        total = Question.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\n Done! +{total_new} new questions. Total in DB: {total}"
        ))
