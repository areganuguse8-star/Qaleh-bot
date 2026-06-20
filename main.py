@dp.message_handler(state=BotStates.chatting_with_ai)
async def chat_with_character(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    character = user_data.get('character', 'ሙሴ')
    user_msg = message.text
    
    if GEMINI_KEY:
        try:
            # ለAI ባህሪ የምንሰጠው ትዕዛዝ (System Prompt)
            prompt = (
                f"አንተ መጽሐፍ ቅዱሳዊው ገጸ-ባህሪ {character} ነህ። "
                f"ከተጠቃሚው ለሚቀርብልህ ጥያቄ ልክ እንደ እሱ ባህሪ ሆነህ በጥበብ፣ በትሕትና፣ "
                f"በመንፈሳዊ እውቀት እና በመጽሐፍ ቅዱስ ታሪክ ላይ ብቻ ተመስርተህ በአማርኛ ቋንቋ ምላሽ ስጥ።"
                f"\n\nተጠቃሚው የጠየቀህ ጥያቄ፦ {user_msg}"
            )
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            await message.reply(response.text)
        except Exception as e:
            await message.reply("⚠️ ይቅርታ፣ ከ AI ሰርቨር ጋር መገናኘት አልተቻለም። እባክዎን ቆይተው ይሞክሩ።")
    else:
        # የጌሚኒ ቁልፍ ከሌለ ቦቱ እንዳይበላሽ የመጠባበቂያ (Fallback) መልእክት
        fallback_responses = {
            "ነቢዩ ሙሴ": f"እኔ የእግዚአብሔር ባሪያ ሙሴ ነኝ። ስለ መራሁት ሕዝብ ወይስ ስለ ሕጉ ማወቅ የምትፈልገው ምንድን ነው? (ማሳሰቢያ፦ የ AI መገናኛ ቁልፍ ስላልተገጠመ የተሟላ ምላሽ መስጠት አልቻልኩም)።",
            "ንጉሥ ሰሎሞን": f"ሰላም ለአንተ ይሁን ልጄ። እግዚአብሔር ከሰጠኝ ጥበብ ምን ማወቅ ትሻለህ? (ማሳሰቢያ፦ የ AI መገናኛ ቁልፍ ስላልተገጠመ የተሟላ ምላሽ መስጠት አልቻልኩም)።"
        }
        await message.reply(fallback_responses.get(character))

# 7. ቦቱን በሰርቨር ላይ የማስነሻ መንገዶች (Webhook & Polling)
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if name == 'main':
    if os.environ.get('RENDER_EXTERNAL_URL'):
        # በCloud/Render ላይ ሲሆን Webhook ይጠቀማል
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        # በኮምፒውተር ወይም በስልክ ለሙከራ Run ሲደረግ
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
