from pydantic import BaseSettings


class Settings(BaseSettings):
    # DATABASE_URL: str = 'mysql+aiomysql://root:root@127.0.0.1:3306/test?charset=utf8mb4'
    pconfig = {
        "proxyUser": "bubbleai",
        "proxyPass": "bubbleai",
        "proxyHost": "proxy.smartproxycn.com",
        "proxyPort": "1000",
    }
    proxies = {
        "http": "http://{}:{}@{}:{}".format(
            pconfig["proxyUser"],
            pconfig["proxyPass"],
            pconfig["proxyHost"],
            pconfig["proxyPort"],
        ),
        "https": "http://{}:{}@{}:{}".format(
            pconfig["proxyUser"],
            pconfig["proxyPass"],
            pconfig["proxyHost"],
            pconfig["proxyPort"],
        ),
    }

    DATABASE_URL: str = "mysql://root:root@192.168.50.2:3306/test?charset=utf8mb4"
     
    # DATABASE_URL: str = "mysql://cb:cryptoBricks123@34.218.139.166:3306/cryptoblab?charset=utf8mb4"
    # KAFKA_URL: str = "172.31.29.203:9092"
    KAFKA_URL: str = "192.168.50.2:9092"
    # BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAB3%2FkAEAAAAA4xXgY8ZDppgup5hb6rSeL1Cx%2B2Q%3DgR09yTCiZ2Ih17Vwj9XIXIEOt9bH29eU8YzJKVKAimYqQFMc2k"
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKf%2FjgEAAAAAuuCHME18p9z74uj%2FXIpG4So5mH0%3DjI4MUyTFTEICCJIRTe0i7Rk1NMG2Y520sh8ChdCD1D0Ui7pSvd"
    STREAM_RULES = '{"value":{"1":"from:BitcoinMagazine","2":"from:LitecoinProject","3":"from:bnbchain","4":"from:neo_blockchain","6":"from:EosNFoundation","13":"from:omgnetworkhq","14":"from:0xproject","16":"from:kybernetwork","17":"from:funtoken_io","24":"from:electriccoinco","27":"from:requestnetwork","30":"from:powerledger_io","36":"from:nuls","39":"from:attentiontoken","40":"from:_poetproject","41":"from:BitSharesGroup","45":"from:cardano","51":"from:_pivx","53":"from:Steemit","54":"from:bluzellehq","57":"from:NEMofficial","59":"from:Syscoin","70":"from:ardorplatform","74":"from:ravencoin","79":"from:fetch_ai","81":"from:0xPolygon","87":"from:AlgoFoundation","90":"from:Ankr","91":"from:WINkLink","92":"from:Contentos","93":"from:CocosBCX","96":"from:chiliz","97":"from:bandprotocol","100":"from:nkn_org","107":"from:originprotocol","108":"from:drepofficial","109":"from:wazirxindia","121":"from:pNetworkDefi","122":"from:TendiesCrypto","134":"from:iearnfinance","135":"from:defi_just","136":"from:projectserum","138":"from:curvefinance","139":"from:thesandboxgame","146":"from:paxosglobal","147":"from:NexusMutual","150":"from:sushiswap","151":"from:dfimoney","157":"from:Wing_Finance","162":"from:AvalancheAVAX","166":"from:secretnetwork","167":"from:pancakeswap","171":"from:alphaventuredao","177":"from:AERGO_IO","179":"from:ShentuChain","180":"from:Akropolis","181":"from:Keep3rV1K","182":"from:Axie Infinity","183":"from:Kava Lend","188":"from:unifiprotocol","197":"from:juventusfc","198":"from:PSG_inside","208":"from:nervosnetwork","214":"from:isafepal","222":"from:badgerdao","223":"from:Stafi_Protocol","230":"from:Conflux","236":"from:shibtoken","238":"from:arweaveteam","239":"from:polkastarter","240":"from:MdexTech","241":"from:realmasknetwork","243":"from:singularity_net","244":"from:automatanetwork","246":"from:tornadocash","247":"from:ethernitychain","249":"from:barn_bridge","258":"from:raydiumprotocol","264":"from:dydx","269":"from:lootproject","270":"from:radicle_xyz","273":"from:blox_staking","274":"from:OfficialSSLazio","275":"from:tranchess","276":"from:Mines of Dalarnia","277":"from:BinaryX","279":"from:ManCityCatala","282":"from:fcporto","284":"from:amptoken","287":"from:rendertoken","288":"from:alchemixfi","289":"from:SantosFC","293":"from:VoxiesNFT\\/","295":"from:convexfinance","296":"from:constitutiondao","297":"from:ookitrade","302":"from:moonbeamnetwork","305":"from:Acala Token","308":"from:AlpineF1Team","311":"from:STEPNofficial","314":"from:Biswap_DEX","320":"from:lidofinance","321":"from:ellipsisfi","327":"from:PolymeshNetwork","328":"from:aptoslabs"},"tag":{"1":"BTCUSDT","2":"LTCUSDT","3":"BNBUSDT","4":"NEOUSDT","6":"EOSUSDT","13":"OMGUSDT","14":"ZRXUSDT","16":"KNCUSDT","17":"FUNUSDT","24":"ZECUSDT","27":"REQUSDT","30":"POWRUSDT","36":"NULSUSDT","39":"BATUSDT","40":"POEUSDT","41":"BTSUSDT","45":"ADAUSDT","51":"PIVXUSDT","53":"STEEMUSDT","54":"BLZUSDT","57":"XEMUSDT","59":"SYSUSDT","70":"ARDRUSDT","74":"RVNUSDT","79":"FETUSDT","81":"MATICUSDT","87":"ALGOUSDT","90":"ANKRUSDT","91":"WINUSDT","92":"COSUSDT","93":"COCOSUSDT","96":"CHZUSDT","97":"BANDUSDT","100":"NKNUSDT","107":"OGNUSDT","108":"DREPUSDT","109":"WRXUSDT","121":"PNTUSDT","122":"GBPUSDT","134":"YFIUSDT","135":"JSTUSDT","136":"SRMUSDT","138":"CRVUSDT","139":"SANDUSDT","146":"PAXGUSDT","147":"WNXMUSDT","150":"SUSHIUSDT","151":"YFIIUSDT","157":"WINGUSDT","162":"AVAXUSDT","166":"SCRTUSDT","167":"CAKEUSDT","171":"ALPHAUSDT","177":"AERGOUSDT","179":"CTKUSDT","180":"AKROUSDT","181":"KP3RUSDT","182":"AXSUSDT","183":"HARDUSDT","188":"UNFIUSDT","197":"JUVUSDT","198":"PSGUSDT","208":"CKBUSDT","214":"SFPUSDT","222":"BADGERUSDT","223":"FISUSDT","230":"CFXUSDT","236":"SHIBUSDT","238":"ARUSDT","239":"POLSUSDT","240":"MDXUSDT","241":"MASKUSDT","243":"AGIXUSDT","244":"ATAUSDT","246":"TORNUSDT","247":"ERNUSDT","249":"BONDUSDT","258":"RAYUSDT","264":"DYDXUSDT","269":"AGLDUSDT","270":"RADUSDT","273":"SSVUSDT","274":"LAZIOUSDT","275":"CHESSUSDT","276":"DARUSDT","277":"BNXUSDT","279":"CITYUSDT","282":"PORTOUSDT","284":"AMPUSDT","287":"RNDRUSDT","288":"ALCXUSDT","289":"SANTOSUSDT","293":"VOXELUSDT","295":"CVXUSDT","296":"PEOPLEUSDT","297":"OOKIUSDT","302":"GLMRUSDT","305":"ACAUSDT","308":"ALPINEUSDT","311":"GMTUSDT","314":"BSWUSDT","320":"LDOUSDT","321":"EPXUSDT","327":"POLYXUSDT","328":"APTUSDT"}}'
    PROXY_USER: str = "cryptobricks_ip-103.179.160.143"
    PROXY_PASS: str = "outbbs54"
    PROXY_HOST: str = "proxy.smartproxycn.com"
    PROXY_PORT: str = "2000"
    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    # PROXY = "http://{}:{}@{}:{}".format(pconfig['proxyUser'], pconfig['proxyPass'], pconfig['proxyHost'], pconfig['proxyPort'])
    # "https": "http://{}:{}@{}:{}".format(pconfig['proxyUser'], pconfig['proxyPass'], pconfig['proxyHost'], pconfig['proxyPort'])
    PROXY: str = "http://{}:{}@{}:{}".format(
        PROXY_USER, PROXY_PASS, PROXY_HOST, PROXY_PORT
    )

    # MTA0MDIyNzI3MzA5OTQ1NjU3Mg.Gww948.GyPlg7KJ_4cd6YCAP0GTb8Ut3UHA7z6fauqAaY
    # MTAzNDM2MzQ5NzkxMzUyNDI1NA.GMsnAm.aMpP4domQ5aAJUqC_Crv8lJxExr6UtttH8stzM
    # test MTA0MzgyMzM5NjYyNDAxMTMyNA.GUZpQu.DUa8eBm7ukfT2hJFdYrfD3XWVZRinRnGvg0jlQ
    # https://discord.com/api/oauth2/authorize?client_id=1040967105459269652&permissions=8&scope=bot
    # https://discord.com/api/oauth2/authorize?client_id=1040227273099456572&permissions=8&scope=bot


settings = Settings()
