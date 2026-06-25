from fontTools.ttLib import TTFont

# OTF 파일 로드 (경로에 맞게 수정)
font = TTFont('stimuli/FandolKai-Regular.otf')

# TTF 포맷으로 저장
font.save('stimuli/FandolKai-Regular.ttf')
print("변환 완료!")