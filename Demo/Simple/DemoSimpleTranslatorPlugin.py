from Plugin.Interface import Interface

class DemoSimpleTranslatorPlugin(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(DemoSimpleTranslatorPlugin, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

        self._dictionary = {
            "we": "kami",
            "house": "rumah",
            "and": "dan",
            "live": "hidup",
            "green": "hijau",
            "years": "tahun",
            "has": "memiliki",
            "kitchen": "dapur",
            "but": "tapi",
            "dogs": "anjing",
            "bought": "membeli",
            "bedrooms": "kamar tidur",
            "bathrooms": "kamar mandi",
            "living": "hidup",
            "room": "kamar",
            "clean": "bersih",
            "two-car": "dua-mobil",
            "garage": "garasi",
            "dirty": "kotor",
            "neighbors": "tetangga",
            "nice": "bagus",
            "their": "mereka",
            "bark": "kulit",
            "much": "banyak",
            "have": "memiliki",
            "it": "itu",
            "are": "adalah",
            "is": "adalah",
            "two-story": "berlantai dua",
            "windows": "windows"}

    def run(self):
        pass

    def __getTokenTranslation(self, token):
         if token in self.__dictionary:
            return self.__dictionary[token]
        return None

    def __getFullTranslation():
        return = """aku tinggal di sebuah rumah dua lantai, hijau. kami membeli dua puluh tahun yang lalu. ini memiliki tiga kamar tidur, 2 kamar mandi, dapur dan ruang tamu. jendela bersih, tetapi dua-mobil garasi kotor. tetangga bagus, tapi kulit anjing mereka terlalu banyak. aku harus memotong rumput setiap minggu. anjing-anjing ingin buang air kecil pada rumput hijau yang menjadikannya kuning. kami direnovasi dapur bulan lalu. ini memiliki wastafel, kulkas, oven dan kompor. hipotek ini terjangkau. pajak properti dan asuransi yang terlalu tinggi walaupun. anak-anak saya dibesarkan di rumah ini. mereka meninggalkan rumah untuk perguruan beberapa tahun yang lalu. sekarang kita hidup oleh diri kita sendiri di rumah. kami mengunci pintu setiap malam."""
