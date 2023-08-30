import pandas as pd
import copy
import pydash as pydash
from datetime import datetime
import openpyxl
import datetime as dt
import json
#Рабочий файл
link = "testActualRLCS.xlsx"
#Константы
K_CONST = 43 #Максимальное изменение рейтинга команды за игру (43)
ROWS = 15000 #19310 #Количество строк в файле #18194 до NASpringCup #19035 до EUSpringCup 15000 для 80%
GAMMA = 2 #Гамма коррекция (2)
Results = 0
PredictedResults = 0
p1 = ""
p2 = ""
p3 = ""
s1 = 0
s2 = 0
s3 = 0

#Функция шанса на победу победившей команды
def chanceWin(team1, team2):
    Rw = 0
    Rl = 0
    for i in Teams[winner]["Players"].keys():
        Rw += Teams[winner]["Players"][i]["rating"]
    for i in Teams[loser]["Players"].keys():
        Rl += Teams[loser]["Players"][i]["rating"]
    Rw = Rw / 3
    Rl = Rl / 3
    if abs(Rl - Rw) < 799: 
        Ew = 1 / (1 + 10**((Rl-Rw)/400))
    elif Rl > Rw:
        Ew = 0.01
    else:
        Ew = 0.99
    if Ew > 0.5:
        global PredictedResults
        PredictedResults+=1
    global Results
    Results+=1
#    print(Results)
#    print(Results)
#    print("Шанс победы команды", team1, "VS", team2, "=", Ew)    
    return Ew

#Функция фактического вклада игрока
def playerImpact(player_score, mate1_score, mate2_score):
    Impact = player_score / (player_score + mate1_score + mate2_score)
    return Impact

#Функция ожидаемого вклада игрока
def playerExpectedImpact(player_rating, mate1_rating, mate2_rating):
    Expected = player_rating / (player_rating + mate1_rating + mate2_rating)
    return Expected

#Функция изменения рейтинга для игрока
def playerChangePlusRating(team, player, player_score, mate1_score, mate2_score, mate1_rating, mate2_rating):
    return (playerImpact(player_score, mate1_score, mate2_score)**GAMMA / playerExpectedImpact(Teams[team]["Players"][player]["rating"], mate1_rating, mate2_rating))

#Сопоставление игроков
def playerSort(team, player1, score1, player2, score2, player3, score3):
    for i in range(1,4):
        count = 1
        for j in Teams[team]["Players"].keys():
            if j == locals()["player"+str(i)]:
                globals()["p"+str(count)] = j
                globals()["s"+str(count)] = locals()["score"+str(i)] 
                count = 1
                break
            else:
                count += 1
    return p1, s1, p2, s2, p3, s3

#Функция проверки наличия игрока в списке и его принадлежность к команде
def playerCheck(name:str, team:str):
    for player in PlayersTeams.keys():
        if name == player:
            if PlayersTeams[player] == team:
                return 1 #Ранее играл в этой же команде
            else:
                oldTeam = PlayersTeams[player]
#               PlayersTeams[player] = team        #Нельзя менять тут, иначе неправильно работает при повторном вызове
                return oldTeam #Ранее играл за oldTeam
#    PlayersTeams[name] = team    #Нельзя менять тут, иначе неправильно работает при повторном вызове
    return 0#Ранее не был известен

#Функция поиска игрока, которого заменили
def rosterMove(team, player:str, mate1:str, mate2:str, oldteam, lastplayed:str):
    if oldteam == 0:
        for i in Teams[team]["Players"].keys():
            if (i != mate1) and (i != mate2):
                Teams["FreePlayers"]["Players"][i] = copy.deepcopy(Teams[team]["Players"][i])
                PlayersTeams[i] = "FreePlayers"
                Teams[team]["Players"].pop(i, "Игрока нет в данной команде")
                Teams[team]["Players"][player] = {
                            "rating": 1500,
                            "q": 350,
                            "lastplayed": lastplayed                    
                }
                PlayersTeams[player] = team
                return
        #Если нет лишнего игрока в команде, которого заменяешь 
        Teams[team]["Players"][player] = {
                    "rating": 1500,
                    "q": 350,
                    "lastplayed": lastplayed                    
        }
        PlayersTeams[player] = team
        return
    else:
        for i in Teams[team]["Players"].keys():
            if (i != mate1) and (i != mate2):
                Teams["FreePlayers"]["Players"][i] = copy.deepcopy(Teams[team]["Players"][i])
                PlayersTeams[i] = "FreePlayers"
                Teams[team]["Players"].pop(i, "Игрока нет в данной команде")
                Teams[team]["Players"][player] = copy.deepcopy(Teams[oldteam]["Players"][player])
                Teams[oldteam]["Players"].pop(player, "Такого игрока нет в старой команде")
                PlayersTeams[player] = team
                return
        #Если нет лишнего игрока в команде, которого заменяешь
        Teams[team]["Players"][player] = copy.deepcopy(Teams[oldteam]["Players"][player])
        Teams[oldteam]["Players"].pop(player, "Такого игрока нет в старой команде")
        PlayersTeams[player] = team
        return
#Функция добавления нового состава
def newTeam(team, player:str, mate1:str, mate2:str, oldteam, lastplayed:str):
    if oldteam == 0:
        Teams[team]["Players"][player] = {
            "rating": 1500,
            "q": 350,
            "lastplayed": lastplayed                    
        }
        PlayersTeams[player] = team
        return
    else:
        Teams[team]["Players"][player] = copy.deepcopy(Teams[oldteam]["Players"][player])
        Teams[oldteam]["Players"].pop(player, "Такого игрока нет в старой команде")
        PlayersTeams[player] = team
        return

#Функция проверки наличия команды и игроков в ней (с присвоением рейтинга для новых)
def teamCheck(team:str, player1:str, player2:str, player3:str, lastplayed:str):
    for teams in Teams.keys(): #Если такая команда существует.
        if team == teams:
            if playerCheck(player1, team) == 1 and playerCheck(player2, team) == 1 and playerCheck(player3, team) == 1:
                return #print("Команда в тех же составах")
            if playerCheck(player1, team) !=1:
                rosterMove(team, player1, player2, player3, playerCheck(player1, team), lastplayed)
            if playerCheck(player2, team) !=1:
                rosterMove(team, player2, player1, player3, playerCheck(player2, team), lastplayed)
            if playerCheck(player3, team) !=1:
                rosterMove(team, player3, player1, player2, playerCheck(player3, team), lastplayed)
            return #print("Изменения состава произведены")
#Если такой команды не нашлось
    Teams[team] = {"Players":{}}  
    if playerCheck(player1, team) == 0 and playerCheck(player2, team) == 0 and playerCheck(player3, team) == 0:          
        Teams[team] = {
            "Players":{
                player1:{
                    "rating": 1500,
                    "q": 350,
                    "lastplayed": lastplayed
                },
                player2:{
                    "rating": 1500,
                    "q": 350,
                    "lastplayed": lastplayed
                },
                player3:{
                    "rating": 1500,
                    "q": 350,
                    "lastplayed": lastplayed
                }
            }
        }
        PlayersTeams[player1] = team
        PlayersTeams[player2] = team
        PlayersTeams[player3] = team
        return #print("Полностью новая команда")
    newTeam(team, player1, player2, player3, playerCheck(player1, team), lastplayed)
    newTeam(team, player2, player1, player3, playerCheck(player2, team), lastplayed)
    newTeam(team, player3, player1, player2, playerCheck(player3, team), lastplayed)
    return #print("Состав добавлен")

#Функция изменения рейтинга после игры
def gamePlayed (winner, loser, pW1_name, pW1_score, pW2_name, pW2_score, pW3_name, pW3_score, pL1_name, pL1_score, pL2_name, pL2_score, pL3_name, pL3_score, game_date):
    Ew = chanceWin(winner, loser)
    plus = K_CONST * (1 - Ew)
    minus = K_CONST * (0 - (1-Ew))
    #playerWinsRatings = copy.deepcopy(Teams[winner]["Players"])
    #playerLoseRatings = copy.deepcopy(Teams[loser]["Players"])
   # print(playerWinsRatings)
   # print(playerLoseRatings)
    pW1_name, pW1_score, pW2_name, pW2_score, pW3_name, pW3_score = playerSort(winner, pW1_name, pW1_score, pW2_name, pW2_score, pW3_name, pW3_score)
    pL1_name, pL1_score, pL2_name, pL2_score, pL3_name, pL3_score = playerSort(loser, pL1_name, pL1_score, pL2_name, pL2_score, pL3_name, pL3_score)
    kw1 = playerChangePlusRating(winner, pW1_name, pW1_score, pW2_score, pW3_score, Teams[winner]["Players"][pW2_name]["rating"], Teams[winner]["Players"][pW3_name]["rating"])
    kw2 = playerChangePlusRating(winner, pW2_name, pW2_score, pW1_score, pW3_score, Teams[winner]["Players"][pW1_name]["rating"], Teams[winner]["Players"][pW3_name]["rating"])
    kw3 = playerChangePlusRating(winner, pW3_name, pW3_score, pW1_score, pW2_score, Teams[winner]["Players"][pW1_name]["rating"], Teams[winner]["Players"][pW2_name]["rating"])
    kl1 = 1/playerChangePlusRating(loser, pL1_name, pL1_score, pL2_score, pL3_score, Teams[loser]["Players"][pL2_name]["rating"], Teams[loser]["Players"][pL3_name]["rating"])
    kl2 = 1/playerChangePlusRating(loser, pL2_name, pL2_score, pL1_score, pL3_score, Teams[loser]["Players"][pL1_name]["rating"], Teams[loser]["Players"][pL3_name]["rating"])
    kl3 = 1/playerChangePlusRating(loser, pL3_name, pL3_score, pL1_score, pL2_score, Teams[loser]["Players"][pL1_name]["rating"], Teams[loser]["Players"][pL2_name]["rating"])
    xW = (plus * 3) / (kw1 + kw2 + kw3)
    xL = (minus * 3) / (kl1 + kl2 + kl3)
    for n in range(1, 4):
        playerW = locals()["pW"+str(n)+"_name"]
        playerL =  locals()["pL"+str(n)+"_name"]
        kwn = locals()["kw"+str(n)]
        kln = locals()["kl"+str(n)]
        Teams[winner]["Players"][playerW]["rating"] += kwn * xW
        Teams[loser]["Players"][playerL]["rating"] += kln * xL
    #playerWinsRatings.clear()
    #playerLoseRatings.clear()
#    print(game_date)
    for l in Teams[winner]["Players"].keys():
        Teams[winner]["Players"][l]["lastplayed"] = game_date
    for l in Teams[loser]["Players"].keys():
        Teams[loser]["Players"][l]["lastplayed"] = game_date
    return #print("Ранги изменены")

#Функция предсказания результата
def predict (team1:str, team2:str):
    r1 = 0
    r2 = 0
    for i in Teams[team1]["Players"].keys():
        r1 += Teams[team1]["Players"][i]["rating"]
    for i in Teams[team2]["Players"].keys():
        r2 += Teams[team2]["Players"][i]["rating"]
    r1 = r1 / 3
    r2 = r2 / 3
    if abs(r2 - r1) < 799: 
        Ew = 1 / (1 + 10**((r2-r1)/400))
    elif r2 > r1:
        Ew = 0.01
    else:
        Ew = 0.99
    print("Шанс победы команды", team1, "VS", team2, "=", Ew)
    if Ew > 0.50:
        return team1, team2
    else:
        return team2, team1
#Функция предсказания турнира дабл элеминэйт на 16 команж
def doubleElPrediction16Teams(t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16):
    print("Первый раунд верхней сетки------------------------------------")
    uW1, uL1 = predict(t1, t16)
    uW2, uL2 = predict(t8, t9)
    uW3, uL3 = predict(t4, t13)
    uW4, uL4 = predict(t5, t12)
    uW5, uL5 = predict(t2, t15)
    uW6, uL6 = predict(t7, t10)
    uW7, uL7 = predict(t3, t14)
    uW8, uL8 = predict(t6, t11)
    print("Первый раунд нижней сетки------------------------------------")
    dW1, dL1 = predict(uL1, uL2)
    dW2, dL2 = predict(uL3, uL4)
    dW3, dL3 = predict(uL5, uL6)
    dW4, dL4 = predict(uL7, uL8)
    print("Второй раунд верхней сетки------------------------------------")
    uW9, uL9 = predict(uW1, uW2)
    uW10, uL10 = predict(uW3, uW4)
    uW11, uL11 = predict(uW5, uW6)
    uW12, uL12 = predict(uW7, uW8)
    print("Второй раунд нижней сетки------------------------------------")
    dW5, dL5 = predict(uL12, dW1)
    dW6, dL6 = predict(uL11, dW2)
    dW7, dL7 = predict(uL10, dW3)
    dW8, dL8 = predict(uL9, dW4)
    print("Третий раунд нижней сетки------------------------------------")
    dW9, dL9 = predict(dW5, dW6)
    dW10, dL10 = predict(dW7, dW8)
    print("Полуфинальный раунд верхней сетки------------------------------------")
    uW13, uL13 = predict(uW9, uW10)
    uW14, uL14 = predict(uW11, uW12)
    print("Четвертый раунд нижней сетки------------------------------------")
    dW11, dL11 = predict(uL13, dW9)
    dW12, dL12 = predict(uL14, dW10)
    print("Полуфинальный раунд нижней сетки------------------------------------")
    dW13, dL13 = predict(dW11, dW12)
    print("Финальный раунд верхней сетки------------------------------------")
    uW15, uL15 = predict(uW13, uW14)
    print("Финальный рауннд нижней сетки------------------------------------")
    dW16, dL16 = predict(uL15, dW13)
    print("Гранд Финал------------------------------------")
    gfW, gfL = predict(uW15, dW16)
#Полное предсказание NASpringCup
def NASpringCup(): 
    print("Первый раунд верхней сетки------------------------------------")
    uW1, uL1 = predict("COMPLEXITY", "TEAM AXLE")
    uW2, uL2 = predict("REBELLION", "VERSION1")
    uW3, uL3 = predict("G2", "KOI")
    uW4, uL4 = predict("OPTIC", "M80")
    uW5, uL5 = predict("FAZE CLAN", "ZERO2ONE")
    uW6, uL6 = predict("DIGNITAS", "FURIA")
    uW7, uL7 = predict("GENGMOBIL1", "HEY BRO")
    uW8, uL8 = predict("SPACESTATION", "NRG")
    print("Первый раунд нижней сетки------------------------------------")
    dW1, dL1 = predict(uL1, uL2)
    dW2, dL2 = predict(uL3, uL4)
    dW3, dL3 = predict(uL5, uL6)
    dW4, dL4 = predict(uL7, uL8)
    print("Второй раунд верхней сетки------------------------------------")
    uW9, uL9 = predict(uW1, uW2)
    uW10, uL10 = predict(uW3, uW4)
    uW11, uL11 = predict(uW5, uW6)
    uW12, uL12 = predict(uW7, uW8)
    print("Второй раунд нижней сетки------------------------------------")
    dW5, dL5 = predict(uL12, dW1)
    dW6, dL6 = predict(uL11, dW2)
    dW7, dL7 = predict(uL10, dW3)
    dW8, dL8 = predict(uL9, dW4)
    print("Третий раунд нижней сетки------------------------------------")
    dW9, dL9 = predict(dW5, dW6)
    dW10, dL10 = predict(dW7, dW8)
    print("Полуфинальный раунд верхней сетки------------------------------------")
    uW13, uL13 = predict(uW9, uW10)
    uW14, uL14 = predict(uW11, uW12)
    print("Четвертый раунд нижней сетки------------------------------------")
    dW11, dL11 = predict(uL13, dW9)
    dW12, dL12 = predict(uL14, dW10)
    print("Полуфинальный раунд нижней сетки------------------------------------")
    dW13, dL13 = predict(dW11, dW12)
    print("Финальный раунд верхней сетки------------------------------------")
    uW15, uL15 = predict(uW13, uW14)
    print("Финальный рауннд нижней сетки------------------------------------")
    dW16, dL16 = predict(uL15, dW13)
    print("Гранд Финал------------------------------------")
    gfW, gfL = predict(uW15, dW16)    
#Симуляция NASpringCUP по каждому раунду (С учетом того, кто выигрывал на самом деле)
def modelNASpringCupRoundByRound():
    print("Первый раунд верхней сетки------------------------------------")
    uW1, uL1 = predict("COMPLEXITY", "TEAM AXLE")
    uW2, uL2 = predict("REBELLION", "VERSION1")
    uW3, uL3 = predict("G2", "KOI")
    uW4, uL4 = predict("OPTIC", "M80")
    uW5, uL5 = predict("FAZE CLAN", "ZERO2ONE")
    uW6, uL6 = predict("DIGNITAS", "FURIA")
    uW7, uL7 = predict("GENGMOBIL1", "HEY BRO")
    uW8, uL8 = predict("SPACESTATION", "NRG")
    print("Второй раунд верхней сетки------------------------------------")
    uW9, uL9 = predict("COMPLEXITY", "VERSION1")
    uW10, uL10 = predict("G2", "OPTIC")
    uW11, uL11 = predict("FAZE CLAN", "FURIA")
    uW12, uL12 = predict("GENGMOBIL1", "SPACESTATION")
    print("Первый раунд нижней сетки------------------------------------")
    dW1, dL1 = predict("TEAM AXLE", "REBELLION")
    dW2, dL2 = predict("KOI", "M80")
    dW3, dL3 = predict("ZERO2ONE", "DIGNITAS")
    dW4, dL4 = predict("HEY BRO", "NRG")
    print("Второй раунд нижней сетки------------------------------------")
    dW5, dL5 = predict("GENGMOBIL1", "REBELLION")
    dW6, dL6 = predict("FAZE CLAN", "KOI")
    dW7, dL7 = predict("G2", "DIGNITAS")
    dW8, dL8 = predict("COMPLEXITY", "NRG")
    print("Третий раунд нижней сетки------------------------------------")
    dW9, dL9 = predict("REBELLION", "FAZE CLAN")
    dW10, dL10 = predict("G2", "NRG")
    print("Полуфинальный раунд верхней сетки------------------------------------")
    uW13, uL13 = predict("VERSION1", "OPTIC")
    uW14, uL14 = predict("FURIA", "SPACESTATION")
    print("Четвертый раунд нижней сетки------------------------------------")
    dW11, dL11 = predict("OPTIC", "FAZE CLAN")
    dW12, dL12 = predict("FURIA", "NRG")
    print("Полуфинальный раунд нижней сетки------------------------------------")
    dW13, dL13 = predict("FAZE CLAN", "NRG")
    print("Финальный раунд верхней сетки------------------------------------")
    uW15, uL15 = predict("VERSION1", "SPACESTATION")
    print("Финальный рауннд нижней сетки------------------------------------")
    dW16, dL16 = predict("FAZE CLAN", "SPACESTATION")
    print("Гранд Финал------------------------------------")
    gfW, gfL = predict("VERSION1", "FAZE CLAN")
#------------------------------------------------------------------------------------------------------------
#Создаем пару словарей с командами
Teams = {
    # "FazeClan": {
    #     "Players":{
    #         "Firstkiller":{
    #             "rating": 1600,
    #             "q": 350,
    #             "lastplayed": dt.date(2021, 12, 12)
    #         },
    #          "Sypical":{
    #             "rating": 1500,
    #             "q": 350,
    #             "lastplayed": dt.date(2021, 12, 12)
    #         },
    #          "mist":{
    #             "rating": 1500,
    #             "q": 350,
    #             "lastplayed": dt.date(2021, 12, 12)
    #         }
    #     }
    # },
    # "Version1":{
    #     "Players":{
    #         "comm":{
    #             "rating": 1500,
    #             "q": 350,
    #             "lastplayed": dt.date(2021, 12, 12)
    #         },
    #          "BeastMode":{
    #             "rating": 1500,
    #             "q": 350,
    #             "lastplayed": dt.date(2021, 12, 12)
    #         },
    #          "Daniel":{
    #             "rating": 1500,
    #             "q": 50,
    #             "lastplayed": dt.date(2021, 12, 12)
    #         }
    #     }
    # }
}
#Команда игроков без команды
Teams["FreePlayers"] = {
    "Players":{
    }
}
#Игроки и их команды "FreePlayers" при отсутствии команды
PlayersTeams = {}
#------------------------------------------------------------------------------
#Основная часть
wb = openpyxl.reader.excel.load_workbook(link, data_only = True)
wb.active = 0
sheet = wb.active
for r in range(2, ROWS + 1): # Обучение по данным с файла
    if  sheet['M' + str(r)].value and sheet['O' + str(r)].value and sheet['Q' + str(r)].value and sheet['S' + str(r)].value and sheet['U' + str(r)].value and sheet['W' + str(r)].value:
        winner = sheet['X' + str(r)].value
        loser = sheet['Y' + str(r)].value
        date = str(sheet['E' + str(r)].value)
        if winner == sheet['H' + str(r)].value:
            pW1 = sheet['L' + str(r)].value
            sW1 = int(sheet['M' + str(r)].value)
            pW2 = sheet['N' + str(r)].value
            sW2 = int(sheet['O' + str(r)].value)
            pW3 = sheet['P' + str(r)].value
            sW3 = int(sheet['Q' + str(r)].value)
            pL1 = sheet['R' + str(r)].value
            sL1 = int(sheet['S' + str(r)].value)
            pL2 = sheet['T' + str(r)].value
            sL2 = int(sheet['U' + str(r)].value)
            pL3 = sheet['V' + str(r)].value
            sL3 = int(sheet['W' + str(r)].value)
        else:
            pL1 = sheet['L' + str(r)].value
            sL1 = int(sheet['M' + str(r)].value)
            pL2 = sheet['N' + str(r)].value
            sL2 = int(sheet['O' + str(r)].value)
            pL3 = sheet['P' + str(r)].value
            sL3 = int(sheet['Q' + str(r)].value)
            pW1 = sheet['R' + str(r)].value
            sW1 = int(sheet['S' + str(r)].value)
            pW2 = sheet['T' + str(r)].value
            sW2 = int(sheet['U' + str(r)].value)
            pW3 = sheet['V' + str(r)].value
            sW3 = int(sheet['W' + str(r)].value)
        if winner != loser and sW1 != 0 and sW2 != 0 and sW3 != 0 and sL1 != 0 and sL2 != 0 and sL3 != 0 and pW1 != "RLCS Referee #1" and pW2 != "RLCS Referee #1" and pW3 != "RLCS Referee #1" and pL1 != "RLCS Referee #1" and pL2 != "RLCS Referee #1" and pL3 != "RLCS Referee #1": #Проверка, что матч был реальным
            teamCheck(winner, pW1, pW2, pW3, date)
            teamCheck(loser, pL1, pL2, pL3, date)
            if Teams.get(winner).get("Players").get(pW1) != None and Teams.get(winner).get("Players").get(pW2) != None and Teams.get(winner).get("Players").get(pW3) != None and Teams.get(loser).get("Players").get(pL1) != None and Teams.get(loser).get("Players").get(pL2) != None and Teams.get(loser).get("Players").get(pL3) != None:
                gamePlayed(winner, loser, pW1, sW1, pW2, sW2, pW3, sW3, pL1, sL1, pL2, sL2, pL3, sL3, date)
#print(Teams)
#print(PlayersTeams)
print(PredictedResults, "Угадано из", Results, "=", PredictedResults/Results)
with open ('ratingElo.json', 'w', encoding="utf-8") as file:
    json.dump(Teams, file)
with open ('playersElo.json', 'w', encoding="utf-8") as file:
    json.dump(PlayersTeams, file)
#modelNASpringCupRoundByRound()
#NASpringCup()
#teamCheck("LUNA GALAXY", "Mittaen", "Rezears", "Smokez", "26.05.2023")
#doubleElPrediction16Teams("KARMINE CORP", "TEAM LIQUID", "TEAM VITALITY", "OXYGEN", "G1", "TEAM BDS", "MOIST", "PSG TUNDRA", "SUHHH", "FUFAXDOP", "LUNA GALAXY", "GUILD", "MONACO", "TWO AND A HALF", "FAST 4WD", "DEVIL FRUIT")