# Author: xyb, Diving_Fish
import math
from typing import  Dict, List

import aiohttp
from .maimaidx_music import total_list


scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')


class ChartInfo(object):
    def __init__(self, idNum:str, diff:int, tp:str, achievement:float, ra:int, comboId:int, scoreId:int,
                 title:str, ds:float, lv:str):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.ra = ra
        self.comboId = comboId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv

    def __str__(self):
        return '%-50s' % f'{self.title} [{self.tp}]' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra

    @classmethod
    def from_json(cls, data):
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        return cls(
            idNum=total_list.by_title(data["title"]).id,
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"]
        )



class BestList(object):

    def __init__(self, size:int):
        self.data = []
        self.size = size

    def push(self, elem:ChartInfo):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        self.data.sort()
        self.data.reverse()
        while(len(self.data) > self.size):
            del self.data[-1]

    def pop(self):
        del self.data[-1]

    def __str__(self):
        return '[\n\t' + ', \n\t'.join([str(ci) for ci in self.data]) + '\n]'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


class getBest(object):

    def __init__(self, sdBest:BestList, dxBest:BestList, userName:str, playerRating:int, musicRating:int):
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.userName = self._stringQ2B(userName)
        self.playerRating = playerRating
        self.musicRating = musicRating
        self.rankRating = self.playerRating - self.musicRating
        self._getBestList(sdBest,dxBest,playerRating,userName)
        
        
    def _Q2B(self, uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e: #转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    def _stringQ2B(self, ustring):
        """把字符串全角转半角"""
        return "".join([self._Q2B(uchar) for uchar in ustring])

    def _getCharWidth(self, o) -> int:
        widths = [
            (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
            (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
            (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
            (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
            (120831, 1), (262141, 2), (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    def _coloumWidth(self, s:str):
        res = 0
        for ch in s:
            res += self._getCharWidth(ord(ch))
        return res

    def _changeColumnWidth(self, s:str, len:int) -> str:
        res = 0
        sList = []
        for ch in s:
            res += self._getCharWidth(ord(ch))
            if res <= len:
                sList.append(ch)
        return ''.join(sList)


    def _getRating(self):
        theRa = self.playerRating
        return theRa

    def _getBestList(self, sdBest:BestList, dxBest:BestList, playerRating:int, userName) -> list: 
        sdBest_dict = dict()
        dxBest_dict = dict()
        for num in range(0, len(sdBest)):
            chartInfo = sdBest[num]
            title = chartInfo.title
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 14) + '...'
            achievement = chartInfo.achievement
            scoreRank = chartInfo.scoreId
            if chartInfo.comboId:
                comboId = chartInfo.comboId    
            raBase = f'Base: {chartInfo.ds} -> {chartInfo.ra}'
            sdnum = num + 1
            sdBest_dict[sdnum] = [title, achievement, chartInfo.ra]
            

        for num in range(0, len(dxBest)):
            chartInfo = dxBest[num]
            title = chartInfo.title
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 14) + '...'
            achievement = chartInfo.achievement
            scoreRank = chartInfo.scoreId
            if chartInfo.comboId:
                comboId = chartInfo.comboId    
            raBase = f'Base: {chartInfo.ds} -> {chartInfo.ra}'
            dxnum = num + 1
            dxBest_dict[dxnum] = [title, achievement, chartInfo.ra]

        b40List = [sdBest_dict, dxBest_dict, playerRating, userName]
        self.b40list = b40List
    
    def _getList(self):
        return self.b40list


    



def computeRa(ds: float, achievement:float) -> int:
    baseRa = 15.0
    if achievement >= 50 and achievement < 60:
        baseRa = 5.0
    elif achievement < 70:
        baseRa = 6.0
    elif achievement < 75:
        baseRa = 7.0
    elif achievement < 80:
        baseRa = 7.5
    elif achievement < 90:
        baseRa = 8.0
    elif achievement < 94:
        baseRa = 9.0
    elif achievement < 97:
        baseRa = 9.4
    elif achievement < 98:
        baseRa = 10.0
    elif achievement < 99:
        baseRa = 11.0
    elif achievement < 99.5:
        baseRa = 12.0
    elif achievement < 99.99:
        baseRa = 13.0
    elif achievement < 100:
        baseRa = 13.5
    elif achievement < 100.5:
        baseRa = 14.0

    return math.floor(ds * (min(100.5, achievement) / 100) * baseRa)


async def generate(payload: Dict) -> (list, bool):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        sd_best = BestList(25)
        dx_best = BestList(15)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        for c in sd:
            sd_best.push(ChartInfo.from_json(c))
        for c in dx:
            dx_best.push(ChartInfo.from_json(c))
        b40 = getBest(sd_best, dx_best, obj["nickname"], obj["rating"] + obj["additional_rating"], obj["rating"])._getList()
        return b40, 0
