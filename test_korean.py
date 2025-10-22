from utils import translate_korean_city, search_korean_cities, parse_location_input

print("=== 한글 도시 검색 테스트 ===")
print("서울 ->", translate_korean_city("서울"))
print("부산 ->", translate_korean_city("부산"))
print("도쿄 ->", translate_korean_city("도쿄"))
print("뉴욕 ->", translate_korean_city("뉴욕"))
print("검색 결과(서):", search_korean_cities("서"))
print("검색 결과(도):", search_korean_cities("도"))

location = parse_location_input("서울")
print("파싱 결과(서울):", location)

location2 = parse_location_input("부산")
print("파싱 결과(부산):", location2)

print("✅ 한글 도시 검색 기능 테스트 완료!")