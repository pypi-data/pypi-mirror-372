import random
from mlflow.tracking.context.abstract_context import RunContextProvider


NOM_FR = [
    ("fourmi", "f"),  # ant
    ("singe", "m"),  # ape
    ("vipère", "f"),  # asp
    ("pingouin", "m"),  # auk
    ("bar", "m"),  # bass (poisson)
    ("chauve-souris", "f"),  # bat
    ("ours", "m"),  # bear
    ("abeille", "f"),  # bee
    ("oiseau", "m"),  # bird
    ("sanglier", "m"),  # boar
    ("insecte", "m"),  # bug
    ("veau", "m"),  # calf
    ("carpe", "f"),  # carp
    ("chat", "m"),  # cat
    ("chimpanzé", "m"),  # chimp
    ("cabillaud", "m"),  # cod
    ("poulain", "m"),  # colt
    ("conque", "f"),  # conch
    ("vache", "f"),  # cow
    ("crabe", "m"),  # crab
    ("grue", "f"),  # crane
    ("crocodile", "m"),  # croc
    ("corbeau", "m"),  # crow
    ("petit", "m"),  # cub (bébé animal → "petit")
    ("cerf", "m"),  # deer
    ("biche", "f"),  # doe
    ("chien", "m"),  # dog
    ("dauphin", "m"),  # dolphin
    ("âne", "m"),  # donkey
    ("colombe", "f"),  # dove
    ("canard", "m"),  # duck
    ("anguille", "f"),  # eel
    ("élan", "m"),  # elk
    ("faon", "m"),  # fawn
    ("pinson", "m"),  # finch
    ("poisson", "m"),  # fish
    ("puce", "f"),  # flea
    ("mouche", "f"),  # fly
    ("poulain", "m"),  # foal
    ("volaille", "f"),  # fowl
    ("renard", "m"),  # fox
    ("grenouille", "f"),  # frog
    ("moucheron", "m"),  # gnat
    ("gnu", "m"),  # gnu
    ("chèvre", "f"),  # goat
    ("oie", "f"),  # goose
    ("tétras", "m"),  # grouse
    ("larve", "f"),  # grub
    ("goéland", "m"),  # gull
    ("lièvre", "m"),  # hare
    ("faucon", "m"),  # hawk
    ("poule", "f"),  # hen
    ("porc", "m"),  # hog
    ("cheval", "m"),  # horse
    ("lévrier", "m"),  # hound
    ("geai", "m"),  # jay
    ("petit", "m"),  # kit (bébé animal)
    ("milan", "m"),  # kite (oiseau rapace)
    ("carpe koï", "f"),  # koi
    ("agneau", "m"),  # lamb
    ("alouette", "f"),  # lark
    ("plongeon", "m"),  # loon
    ("lynx", "m"),  # lynx
    ("jument", "f"),  # mare
    ("moucheron", "m"),  # midge
    ("vison", "m"),  # mink
    ("taupe", "f"),  # mole
    ("orignal", "m"),  # moose
    ("mite", "f"),  # moth
    ("souris", "f"),  # mouse
    ("mulet", "m"),  # mule
    ("triton", "m"),  # newt
    ("hibou", "m"),  # owl
    ("bœuf", "m"),  # ox
    ("panda", "m"),  # panda
    ("manchot", "m"),  # penguin
    ("perche", "f"),  # perch
    ("cochon", "m"),  # pig
    ("carlin", "m"),  # pug
    ("caille", "f"),  # quail
    ("bélier", "m"),  # ram
    ("rat", "m"),  # rat
    ("raie", "f"),  # ray
    ("rouge-gorge", "m"),  # robin
    ("kangourou", "m"),  # roo
    ("corbeau", "m"),  # rook
    ("phoque", "m"),  # seal
    ("alose", "f"),  # shad
    ("requin", "m"),  # shark
    ("mouton", "m"),  # sheep
    ("porcelet", "m"),  # shoat
    ("musaraigne", "f"),  # shrew
    ("pie-grièche", "f"),  # shrike
    ("crevette", "f"),  # shrimp
    ("scinque", "m"),  # skink
    ("mouffette", "f"),  # skunk
    ("paresseux", "m"),  # sloth
    ("limace", "f"),  # slug
    ("éperlan", "m"),  # smelt
    ("escargot", "m"),  # snail
    ("serpent", "m"),  # snake
    ("bécassine", "f"),  # snipe
    ("truie", "f"),  # sow
    ("éponge", "f"),  # sponge
    ("calmar", "m"),  # squid
    ("écureuil", "m"),  # squirrel
    ("cerf", "m"),  # stag
    ("destrier", "m"),  # steed (cheval)
    ("hermine", "f"),  # stoat
    ("cigogne", "f"),  # stork
    ("cygne", "m"),  # swan
    ("sternes", "f"),  # tern
    ("crapaud", "m"),  # toad
    ("truite", "f"),  # trout
    ("tortue", "f"),  # turtle
    ("campagnol", "m"),  # vole
    ("guêpe", "f"),  # wasp
    ("baleine", "f"),  # whale
    ("loup", "m"),  # wolf
    ("ver", "m"),  # worm
    ("troglodyte", "m"),  # wren
    ("yak", "m"),  # yak
    ("zèbre", "m"),  # zebra
]


# Adjectifs avec forme masc/fem explicite
ADJ_FR = [
    ("abondant", "abondante"),  # abundant
    ("capable", "capable"),  # able
    ("abrasif", "abrasive"),  # abrasive
    ("adorable", "adorable"),  # adorable
    ("adaptable", "adaptable"),  # adaptable
    ("aventureux", "aventureuse"),  # adventurous
    ("âgé", "âgée"),  # aged
    ("agréable", "agréable"),  # agreeable
    ("ambitieux", "ambitieuse"),  # ambitious
    ("étonnant", "étonnante"),  # amazing
    ("amusant", "amusante"),  # amusing
    ("colérique", "colérique"),  # angry
    ("favorable", "favorable"),  # auspicious
    ("génial", "géniale"),  # awesome
    ("chauve", "chauve"),  # bald
    ("beau", "belle"),  # beautiful
    ("ahuri", "ahurie"),  # bemused
    ("décoré", "décorée"),  # bedecked
    ("grand", "grande"),  # big
    ("amer-doux", "amère-douce"),  # bittersweet
    ("rougissant", "rougissante"),  # blushing
    ("audacieux", "audacieuse"),  # bold
    ("bondissant", "bondissante"),  # bouncy
    ("musclé", "musclée"),  # brawny
    ("brillant", "brillante"),  # bright
    ("robuste", "robuste"),  # burly
    ("animé", "animée"),  # bustling
    ("calme", "calme"),  # calm
    ("compétent", "compétente"),  # capable
    ("insouciant", "insouciante"),  # carefree
    ("capricieux", "capricieuse"),  # capricious
    ("attentionné", "attentionnée"),  # caring
    ("décontracté", "décontractée"),  # casual
    ("charmant", "charmante"),  # charming
    ("détendu", "détendue"),  # chill
    ("classe", "classe"),  # classy
    ("propre", "propre"),  # clean
    ("maladroit", "maladroite"),  # clumsy
    ("coloré", "colorée"),  # colorful
    ("rampant", "rampante"),  # crawling
    ("élégant", "élégante"),  # dapper
    ("distingué", "distinguée"),  # debonair
    ("fougueux", "fougueuse"),  # dashing
    ("défiant", "défiante"),  # defiant
    ("délicat", "délicate"),  # delicate
    ("délicieux", "délicieuse"),  # delightful
    ("éblouissant", "éblouissante"),  # dazzling
    ("efficace", "efficace"),  # efficient
    ("enchanteur", "enchanteresse"),  # enchanting
    ("divertissant", "divertissante"),  # entertaining
    ("enthousiaste", "enthousiaste"),  # enthused
    ("exultant", "exultante"),  # exultant
    ("intrépide", "intrépide"),  # fearless
    ("impeccable", "impeccable"),  # flawless
    ("chanceux", "chanceuse"),  # fortunate
    ("drôle", "drôle"),  # fun / funny
    ("voyant", "voyante"),  # gaudy
    ("doux", "douce"),  # gentle
    ("doué", "douée"),  # gifted
    ("glamour", "glamour"),  # glamorous
    ("grandiose", "grandiose"),  # grandiose
    ("sociable", "sociable"),  # gregarious
    ("beau", "belle"),  # handsome
    ("hilarant", "hilarante"),  # hilarious
    ("honorable", "honorable"),  # honorable
    ("illustre", "illustre"),  # illustrious
    ("incongru", "incongrue"),  # incongruous
    ("indécis", "indécise"),  # indecisive
    ("laborieux", "laborieuse"),  # industrious
    ("intelligent", "intelligente"),  # intelligent
    ("curieux", "curieuse"),  # inquisitive
    ("intrigué", "intriguée"),  # intrigued
    ("invincible", "invincible"),  # invincible
    ("judicieux", "judicieuse"),  # judicious
    ("bienveillant", "bienveillante"),  # kindly
    ("languide", "languide"),  # languid
    ("instruit", "instruite"),  # learned
    ("légendaire", "légendaire"),  # legendary
    ("sympathique", "sympathique"),  # likeable
    ("bruyant", "bruyante"),  # loud
    ("lumineux", "lumineuse"),  # luminous
    ("luxuriant", "luxuriante"),  # luxuriant
    ("lyrique", "lyrique"),  # lyrical
    ("magnifique", "magnifique"),  # magnificent
    ("merveilleux", "merveilleuse"),  # marvelous
    ("masqué", "masquée"),  # masked
    ("mélodieux", "mélodieuse"),  # melodic
    ("miséricordieux", "miséricordieuse"),  # merciful
    ("changeant", "changeante"),  # mercurial
    ("monumental", "monumentale"),  # monumental
    ("mystérieux", "mystérieuse"),  # mysterious
    ("nébuleux", "nébuleuse"),  # nebulous
    ("nerveux", "nerveuse"),  # nervous
    ("vif", "vive"),  # nimble
    ("curieux", "curieuse"),  # nosy
    ("omniscient", "omnisciente"),  # omniscient
    ("ordonné", "ordonnée"),  # orderly
    ("ravi", "ravie"),  # overjoyed
    ("paisible", "paisible"),  # peaceful
    ("peint", "peinte"),  # painted
    ("persévérant", "persévérante"),  # persistent
    ("placide", "placide"),  # placid
    ("poli", "polie"),  # polite
    ("populaire", "populaire"),  # popular
    ("puissant", "puissante"),  # powerful
    ("perplexe", "perplexe"),  # puzzled
    ("turbulent", "turbulente"),  # rambunctious
    ("rare", "rare"),  # rare
    ("rebelle", "rebelle"),  # rebellious
    ("respecté", "respectée"),  # respected
    ("résilient", "résiliente"),  # resilient
    ("vertueux", "vertueuse"),  # righteous
    ("réceptif", "réceptive"),  # receptive
    ("odorant", "odorante"),  # redolent
    ("voyou", "voyou"),  # rogue
    ("grondant", "grondante"),  # rumbling
    ("salé", "salée"),  # salty
    ("impertinent", "impertinente"),  # sassy
    ("secret", "secrète"),  # secretive
    ("sélectif", "sélective"),  # selective
    ("serein", "sereine"),  # sedate
    ("sérieux", "sérieuse"),  # serious
    ("tremblant", "tremblante"),  # shivering
    ("habile", "habile"),  # skillful
    ("sincère", "sincère"),  # sincere
    ("farouche", "farouche"),  # skittish
    ("silencieux", "silencieuse"),  # silent
    ("souriant", "souriante"),  # smiling
    ("fourbe", "fourbe"),  # sneaky
    ("sophistiqué", "sophistiquée"),  # sophisticated
    ("soigné", "soignée"),  # spiffy
    ("majestueux", "majestueuse"),  # stately
    ("suave", "suave"),  # suave
    ("stylé", "stylée"),  # stylish
    ("raffiné", "raffinée"),  # tasteful
    ("réfléchi", "réfléchie"),  # thoughtful
    ("tonitruant", "tonitruante"),  # thundering
    ("voyageur", "voyageuse"),  # traveling
    ("précieux", "précieuse"),  # treasured
    ("confiant", "confiante"),  # trusting
    ("inégalé", "inégalée"),  # unequaled
    ("bouleversé", "bouleversée"),  # upset
    ("unique", "unique"),  # unique
    ("libéré", "libérée"),  # unleashed
    ("utile", "utile"),  # useful
    ("optimiste", "optimiste"),  # upbeat
    ("indiscipliné", "indisciplinée"),  # unruly
    ("précieux", "précieuse"),  # valuable
    ("vanté", "vantée"),  # vaunted
    ("victorieux", "victorieuse"),  # victorious
    ("accueillant", "accueillante"),  # welcoming
    ("fantaisiste", "fantaisiste"),  # whimsical
    ("mélancolique", "mélancolique"),  # wistful
    ("sage", "sage"),  # wise
    ("inquiet", "inquiète"),  # worried
    ("jeune", "jeune"),  # youthful
    ("zélé", "zélée"),  # zealous
]


class FrenchNamesProvider(RunContextProvider):
    def in_context(self):
        # Return True if this context applies
        return True
    
    def run_name(self):
        rng = random.Random()
        nom, genre = rng.choice(NOM_FR)
        adj_m, adj_f = rng.choice(ADJ_FR)
        adj = adj_m if genre == "m" else adj_f
        return f"{nom}-{adj}-{rng.randint(0, 999)}"

    def tags(self):
        return {"mlflow.runName": self.run_name()}
