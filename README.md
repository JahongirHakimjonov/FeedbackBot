1. telegram bot uchun aiogramda yozilgan kod kerak bu kodda login qilish funsiyasi bolishi kerak , start bosilgan vaqtda foydalanuvchidan login_id soralishi kerak id ni yuborgandan keyin password so'ralishi kerak login_id va passowrd posgressql database dagi students table dagi login_id va password column laridan tekshirilishi kerak shunday login_id va password mavjud bo'lsa foydalanuvchining telegram_id raqami students tabledagi telegram_id nomli columnga yozib qoyilish kerak va students tabledagi telegram_id raqami bor foydalanuvchilardan login_id va password so'ralmasligi kerak

2. "Ustozning pedagoglik mahoratiga baho bering" degan habar jonatilishi va bu habar tagida 1 dan 5 gacha bo'lgan gorizontal joylashgan inline tugma bo'lishi kerak va tugama bosilgan dan so'ng "Fikr mulohazalaringizni jo'nating" degan habar yuborilishi kerak va foydalanuvchi yuborgan habarni scores nomili table dagi score_for_teacher va feedback nomli columnlarga yozib qo'yishi kerak va qo'lgan columnlar ham mavjud lesson_id, student_id, teacher_id bu columnlardagi malumotlar shu vaqtda shunday telegram id raqamli foydalanuvchi qaysi dars va kimning darsi bo'layotganini avtomatik aniqlab yozib qo'yishi kerak yuqorigadi habarlar haftaning qaysi kuni va qaysi avqtida jo'natilishini class_schedule nomli tabledagi day va end_time columnlaridan olinishi kerak va foydalanuvchidan score_for_teacher uchun baho va feedback qabul qilish davomiyligi end_time dan boshlab 80 daqiqa davom etsin

3. botda tilini tanlash uchun defolt tugam bo'lishi kerak tillar esa rus uzbek va ingliz tillar bo'lsin yani bot shu 3ta tilda ishlaydigan bo'lishi kerak va "men haqimda" deb nomlangan defolt tugma ham bo'lsin bu tugama bosilganda students nomli table dagi foydalanuvchi telegram id si bilan bir xil bo'lgan qatordagi first_name , last_name, telegram_id nomli columnlardagi malumotlarni

Ism: first_name
Familiya: last_name
Telegram id : telegram_id

ko'rinishda jo'natsin va shu row dagi telegram_id va foydalanuvchining telegram id raqami mosligi tekshirilsin aks holda malumot jo'natilmasin yani ha bir foydalanuvchiga faqat o'zi haqidagi ma'lumot jo'natilsin

4. bot uchun berilgan shartlar va talablarda kamchilik va xatoliklar bo'ladigan bo'sa ularni to'girlash kerak va botni yuqori darajada tez va sifatli ishlaydigan qilish kerak va botni kuchaytirish kerak va botni bir nechta kerakli .py fillerga ajratib yozish kerak



```git pull```

```docker-compose down```

```docker-compose up -d --build```