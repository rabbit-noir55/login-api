from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
 
 
 
 
 
from playwright.sync_api import sync_playwright ,TimeoutError
import requests
import time



def send_image(image_path,url, max_retries=5,):
    for attempt in range(1, max_retries + 1):
        start_time = time.time()
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(url, files=files, timeout=30)

            end_time = time.time()
            print(f"{image_path} --> Urinish {attempt}, vaqt: {end_time - start_time:.2f} sekund")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if "message" in data:
                        print(f"✅ Javob: {data['message']}")
                        return data["message"]
                except Exception:
                    print("⚠️ JSON formatida emas")
            else:
                print(f"❌ Status: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Xatolik: {e}")

          # qayta urinishi oldidan biroz kutadi

    print("❌ 5 urinishdan keyin ham muvaffaqiyatsiz")
    return None


def save_captcha(page, save_path="captcha.png"):
    # captcha img elementini topamiz
    img = page.wait_for_selector('img[alt="captcha image"]', timeout=5000)
    if not img:
        raise Exception("Captcha rasmi topilmadi!")

    # Rasm to‘liq yuklanishini kutamiz (naturalWidth > 0 bo‘lganda tayyor bo‘ladi)
    page.wait_for_function(
        "(img) => img.complete && img.naturalWidth > 0",
        arg=img
    )

    # Faqat rasm elementini screenshot qilish
    img.screenshot(path=save_path)
    print(f"✅ Captcha saqlandi: {save_path}")
def element_ustiga_chiqar(page, selector):
    css_patch = """
        (el) => {
            el.style.position = 'fixed';
            el.style.zIndex = '999999';
            el.style.top = '0';
            el.style.left = '0';
            el.style.pointerEvents = 'auto';
            el.style.visibility = 'visible';
            el.style.opacity = '1';
            el.style.display = 'block';
        }
    """
    try:
        page.eval_on_selector(selector, css_patch)
        print(f"✅ CSS o'zgartirildi: {selector}")
    except Exception as e:
        print(f"⚠️ Xatolik: {e}")
def element_yangilash(page, *, name=None, class_name=None, value=""):
    start = time.time()

    selector = None

    if name:
        selector = f'input[name="{name}"]'
    elif class_name:
        selector = f'input.{class_name}'
    else:
        print("⚠️ name yoki class_name ko'rsatilmagan!")
        return

    try:
        if page.query_selector(selector):
            page.fill(selector, value)
            print(f"✅ Element topildi va qiymat berildi: {selector} = {value}")
        else:
            print(f"❌ Element topilmadi: {selector}")
    except Exception as e:
        print(f"⚠️ Xatolik: {e}")
    
    end = time.time()
    print(f"⏱️ element_yangilash uchun vaqt: {round(end - start, 3)} soniya")


def element_bosish(page, tag="*", value="", **kwargs):
    start = time.time()

    selector = tag

    for attr, attr_value in kwargs.items():
        if attr == "class_name":
            classes = "." + ".".join(attr_value.strip().split())
            selector += classes
        elif attr == "id":
            selector += f'#{attr_value}'
        elif attr.startswith("data_"):
            data_attr = attr.replace("_", "-")
            selector += f'[{data_attr}="{attr_value}"]'
        else:
            selector += f'[{attr.replace("_", "-")}="{attr_value}"]'

    if value and "value" not in kwargs:
        selector += f'[value="{value}"]'

    try:
        element = page.query_selector(selector)
        if element:
            element.click()
            print(f"✅ Bosildi: {selector}")
        else:
            print(f"❌ Topilmadi: {selector}")
    except Exception as e:
        print(f"⚠️ Xatolik: {e}")

    end = time.time()
    print(f"⏱️ element_bosish uchun vaqt: {round(end - start, 3)} soniya")

def get_element_content_by_class(page, class_name: str, timeout: int = 100000) -> str | None:
    selector = f".{class_name}"
    try:
        # 1️⃣ JavaScript orqali DOMga yuklanadigan elementni kutamiz
        page.wait_for_selector(selector, timeout=timeout)

        # 2️⃣ Yuklangach textContent olamiz
        content = page.eval_on_selector(selector, "el => el.textContent.trim()")
        return content
    except TimeoutError:
        print(f"⛔ Element '{class_name}' {timeout} ms ichida topilmadi.")
        return None
def logout(page):
    """
    Sahifadagi logout tugmasini dinamik kutib bosadi.
    """
    try:
        selector = 'form[name="logout"] a.header-links__link'
        
        # Element DOM’da chiqishini dinamik kutish
        link = page.wait_for_selector(selector, state="visible")
        
        # Click qilish
        link.click()
        print("✅ Logout qilindi")
    except Exception as e:
        print(f"❌ Logout tugmasi topilmadi yoki xatolik: {e}")

def header_submenu_click(page, link_test_id: str):
    """
    Header submenu ichidagi <a> elementni data-test-id orqali dinamik kutib bosadi.
    """
    try:
        selector = f'ul.header-submenu a[data-test-id="{link_test_id}"]'
        
        # Element DOM’da chiqishini dinamik kutish
        link = page.wait_for_selector(selector, state="visible")
        
        # Click qilish
        link.click()
        print(f"✅ Bosildi: {link_test_id}")
    except Exception as e:
        print(f"❌ Topilmadi yoki xatolik: {link_test_id} -> {e}")
def is_login_error(page, timeout=3000):
    """
    Login xatolik xabarini tekshiradi.
    Agar 'Parol yoki login notoʻgʻri koʻrsatilgan' yozuvi bo‘lsa True qaytaradi, aks holda False.
    """
    try:
        # Locator orqali elementni olish
        message_div = page.locator('div.message').first
        
        # Agar element ko‘rinsa (timeout kutish)
        message_div.wait_for(state="visible", timeout=timeout)
        
        # Matnni olish
        text = message_div.inner_text().strip()
        
        if "Parol yoki login notoʻgʻri koʻrsatilgan" in text:
            return True
        else:
            return False
    except Exception:
        # Umuman topilmasa ham False qaytaradi
        return False

def ochish(yadro,login,password):
    start = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://login.emaktab.uz/login")
        element_ustiga_chiqar(page,'form.login')

        element_yangilash(page, name='login', value=login)
        element_yangilash(page, name='password', value=password)
        element_bosish(page, tag="input", value="Tizimga kiring")
        if page.url=="https://login.emaktab.uz/login":
            element_ustiga_chiqar(page,'form.login')
            if is_login_error(page):
                end = time.time()
                print(f"\n⏳ Umumiy bajarilish vaqti: {round(end - start, 3)} soniya")
                return False
            save_captcha(page)
            element_yangilash(page,name='Captcha.Input',value=send_image(image_path="captcha.png", url=yadro))
            print("Sarlavha:", page.title())
            element_bosish(page, tag="input", value="Tizimga kiring")
        while True:
            if is_login_error(page):
                end = time.time()
                print(f"\n⏳ Umumiy bajarilish vaqti: {round(end - start, 3)} soniya")
                return False
            elif "userfeed" in page.url:
                break
            elif page.url!="https://login.emaktab.uz/login":
                element_ustiga_chiqar(page,'form.login')
                save_captcha(page)
                element_yangilash(page,name='Captcha.Input',value=send_image("captcha.png"))
                element_bosish(page, tag="input", value="Tizimga kiring")
                print("salom")
          
            
        if "userfeed" in page.url:
            header_submenu_click(page, "Kundalik")
          
            if "marks" in page.url:
                
                logout(page)
            end = time.time()
            print(f"\n⏳ Umumiy bajarilish vaqti: {round(end - start, 3)} soniya")
            return True
        elif is_login_error(page):
            end = time.time()
            print(f"\n⏳ Umumiy bajarilish vaqti: {round(end - start, 3)} soniya")
            return False
        
       
        





@api_view(['GET'])
def salom_view(request):
    login = request.query_params.get('login')
    parol = request.query_params.get('parol')
    yadro = request.query_params.get('yadro')
    yadro=yadro+"/upload/"
    if not login or not parol or not yadro:
        return Response({"error": "login, parol va yadro kerak!"}, status=400)

    return Response({"message": ochish(login=login, password=parol, yadro=yadro) })
@api_view(['GET'])
def salom_vie(request):
    return Response({"message": "Salom"})