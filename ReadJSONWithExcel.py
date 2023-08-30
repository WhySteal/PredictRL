import json
import openpyxl




# Теперь тестируем вывод в лист exel.
book = openpyxl.Workbook()
sheet = book.active
sheet['EA100000'] = ''
sheet['A1'] = 'id'
sheet['B1'] = 'title'
sheet['C1'] = 'playlist'
sheet['D1'] = 'overtime'
sheet['E1'] = 'date'
sheet['F1'] = 'map'
sheet['G1'] = 'duration'
sheet['H1'] = 'blue_team_name'
sheet['I1'] = 'blue_goals'
sheet['J1'] = 'orange_team_name'
sheet['K1'] = 'orange_goals'
sheet['L1'] = 'blue_player_1_name'
sheet['M1'] = 'blue_player_1_score'
sheet['N1'] = 'blue_player_2_name'
sheet['O1'] = 'blue_player_2_score'
sheet['P1'] = 'blue_player_3_name'
sheet['Q1'] = 'blue_player_3_score'
sheet['R1'] = 'orange_player_1_name'
sheet['S1'] = 'orange_player_1_score'
sheet['T1'] = 'orange_player_2_name'
sheet['U1'] = 'orange_player_2_score'
sheet['V1'] = 'orange_player_3_name'
sheet['W1'] = 'orange_player_3_score'
#sheet[1][0].value = "test"
#sheet.cell(row=2,column=1).value = "super test"

row = 2

# Чтение файла
for number in range(508):
    link = 'C:\\RocketLeagueReplays\\ID_JSON_new\\76561199225615730_' + str(number) + '.json'
    print(number)
    with open(link, 'r') as f:
     data = json.load(f)
# Извлечение информации о матчах
    for match in data['list']:
        print(number)
#        if match.get('id') and ('G0' in match.get('replay_title')) == False and match.get('playlist_id') and match.get('overtime') and match.get('date') and match.get('map_name') and match.get('duration') and match.get('duration') > 300 and match['blue'].get('name') and match['orange'].get('name'):
        if match.get('id') and match.get('playlist_id') and match.get('duration') and match.get('duration') > 300 and match['blue'].get('name') and match['orange'].get('name'):
            sheet[row][0].value = match.get('id')
            sheet[row][1].value = match.get('replay_title')
            sheet[row][2].value = match.get('playlist_id')
            sheet[row][3].value = match.get('overtime')
            sheet[row][4].value = match.get('date')
            sheet[row][5].value = match.get('map_name')
            sheet[row][6].value = match.get('duration')
            sheet[row][7].value = match['blue'].get('name')
            sheet[row][8].value = match['blue'].get('goals')
            if match['blue'].get('goals') == None:
                sheet[row][8].value = 0 
            sheet[row][9].value = match['orange'].get('name')
            sheet[row][10].value = match['orange'].get('goals')
            if match['orange'].get('goals') == None:
                sheet[row][10].value = 0 
            blue_players = match['blue'].get('players')
            k = 0
            if (blue_players):
                for player in blue_players:
                    sheet[row][11 + 2*k].value = player['name']
                    sheet[row][12 + 2*k].value = player['score']
                    k+=1
            orange_players = match['orange'].get('players')
            k = 0
            if (orange_players):
                for player in orange_players:
                    sheet[row][17 + 2*k].value = player['name']
                    sheet[row][18 + 2*k].value =player['score']
                    k+=1
            row+=1

book.save('C:\\RocketLeagueReplays\\rlcs_book_newDATA.xlsx')
book.close()
