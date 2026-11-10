"""
우리 집 냉장고 — 최종 단일 파일 앱 — 게임형 전체 선반 / 사용자 지정 캘린더 시각

실행: pip install -r requirements.txt
      streamlit run app.py
GitHub 저장소 최상단에 app.py, requirements.txt를 올리고 Streamlit Community
Cloud에서 app.py를 선택해 배포합니다. 실제 배포/계정 설정은 사용자가 진행합니다.

[가족 공유 영구 저장소]
Supabase 전용 프로젝트 SQL Editor에서 다음 SQL 실행:
create table if not exists public.fridge_records (
 id uuid primary key, kind text not null, payload jsonb not null
);
-- 기존 버전에서 생성한 테이블에도 자석/알림 유형을 허용합니다.
alter table public.fridge_records drop constraint if exists fridge_records_kind_check;
alter table public.fridge_records add constraint fridge_records_kind_check
 check (kind in ('item','shopping','magnet','notification'));
create index if not exists fridge_records_kind_idx on public.fridge_records(kind);
alter table public.fridge_records enable row level security;
revoke all on public.fridge_records from anon, authenticated;
grant all on public.fridge_records to service_role;

Streamlit 배포 설정 Secrets (실제 비밀값은 GitHub 코드에 올리지 마세요):
APP_PASSWORD = "10자이상-가족공용비밀번호"
SUPABASE_URL = "https://본인프로젝트.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "서버용 service_role 키"
APP_URL = "실제로 배포된 HTTPS 앱 주소"

미연결 시 data/fridge.db의 로컬 체험 모드입니다. Cloud 로컬 파일은 재시작 시
사라질 수 있어 실제 가족 사용에는 Supabase가 필수입니다. data 폴더와 실제
secrets.toml은 GitHub에 올리지 마세요. 동시 수정은 마지막 저장이 반영됩니다.
공용 비밀번호 한 가구용이며 로그인 시도 제한/개별 사용자 권한은 없습니다.

[앱 종료 후 휴대폰 알림 — 선택 연동]
텔레그램 앱에서 BotFather로 봇 생성, 각 수신자가 봇 대화를 시작하거나 가족
그룹에 봇 추가 후 chat_id 확인. 토큰/채팅 ID는 공개하지 마세요.
GitHub 저장소 Settings > Secrets and variables > Actions에 아래 4개 등록:
SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, TELEGRAM_BOT_TOKEN,
TELEGRAM_CHAT_IDS (여러 chat_id는 쉼표로 구분)
Actions는 Streamlit Secrets를 읽지 않으므로 별도로 설정해야 합니다.
예약 실행은 GitHub 저장소에 .github/workflows/fridge-alert.yml을 직접 생성하여
아래 내용을 붙여넣습니다. 전달물은 2개이지만 외부 알림에는 이 예약 설정이
추가로 필요합니다. GitHub Actions 기능/사용량 정책은 본인 계정에서 확인하세요.

name: Fridge reminders
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
concurrency:
  group: fridge-reminders
  cancel-in-progress: false
permissions:
  contents: read
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python app.py --notify
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_IDS: ${{ secrets.TELEGRAM_CHAT_IDS }}

기본 브랜치에 저장 후 Actions 탭에서 수동 실행해 연결을 확인합니다.
매일 한국 시간 오전 9시 예정. GitHub 예약은 지연/누락/비활성화될 수 있으며
정시 전송 보장은 아닙니다. 해당 날짜 기준 하루 전/당일만 발송, 놓친 날을
소급 전송하지 않습니다. 9시 이후 등록한 당일 기한은 앱 화면에서 확인하세요.
각 실행 때 DB를 다시 조회해 소진/삭제는 제외하고 변경된 기한을 반영합니다.
전송 직전 수정과 경합하면 이미 발송된 메시지는 회수되지 않습니다.
중복 방지용 예약 기록을 전송 전에 남깁니다. 실패/응답 불명확 시 자동 재전송하지
않으므로 누락 가능성이 있습니다. Actions 실패와 notification 상태를 점검하세요.
필요한 경우 수신 확인 후 해당 예약 기록을 관리자 SQL로 정리하고 수동 재실행하세요.
알림 기록은 자동 삭제하지 않습니다. 필요하면 지난 notification 행을 정리하세요.
텔레그램 알림은 폰의 알림 권한/무음 설정에 영향을 받습니다.

[캘린더 기본 시각]
Streamlit Secrets에 CALENDAR_TIME = "20:00"을 선택적으로 설정할 수 있습니다.
설정/QR에서 고른 시간은 현재 세션에 적용됩니다. 텔레그램 예약 시각은 별개이며
Actions cron 기본값은 한국 시간 오전 9시입니다.

[보조 캘린더]
ICS 파일은 캘린더에 가져온 후 알림 권한/일정을 확인해야 합니다. 앱 수정/소진과
동기화되지 않고 캘린더 앱에 따라 알림을 무시할 수도 있습니다. 자동 푸시가 아닙니다.

[확인]
QR/설정에서 실제 HTTPS 앱 주소로 QR 생성. QR에는 비밀번호가 포함되지 않습니다.
다른 폰에서 사진 등록/데이터 공유/재시작 후 보존/연락처 전화 연결을 확인하세요.
카메라는 HTTPS와 브라우저 권한이 필요하며 안 되면 사진 업로드를 사용하세요.
최대 10MB 사진을 축소 JPEG로 DB에 저장하므로 소규모 가족용입니다.
날짜는 한국 시간 기준. 이름만 필수, 사진/기한 선택. 자세한 정보는 수정에서 변경.
표시 기한/사진/직접 기록한 상태는 안전 보증이나 부패 판정이 아닙니다.

"""
import base64
import io
import json
import sqlite3
import uuid
from datetime import date, datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import requests
from PIL import Image, ImageOps

ZONES = {'냉장실': ['상단 선반', '중단 선반', '채소칸', '문쪽 수납칸'], '냉동실': ['상단 냉동칸', '하단 냉동칸'], '실온': ['식품 보관함']}
STATES = ['괜찮아요', '시들었어요', '곰팡이/이상 있어요', '확인 필요']


def remaining(item, today=None):
    return (date.fromisoformat(item['expiry']) - (today or datetime.now(ZoneInfo('Asia/Seoul')).date())).days if item.get('expiry') else None


def urgency(item, today=None):
    days = remaining(item, today)
    return (days is None, days if days is not None else 999999, item.get('name', ''))


def expiry_label(item, today=None):
    n = remaining(item, today)
    if n is None:
        return '기한 미입력 · 포장지 확인'
    if n < 0:
        return f'표시 기한 {abs(n)}일 지남 · 상태 확인'
    if n == 0:
        return '표시 기한 오늘 · 상태 확인'
    return f'표시 기한까지 {n}일'


def photo_encode(file):
    if not file:
        return None
    if file.size > 10 * 1024 * 1024:
        raise ValueError('사진은 10MB 이하로 올려 주세요.')
    with Image.open(file) as im:
        if im.width * im.height > 30_000_000:
            raise ValueError('사진 해상도가 너무 큽니다. 작은 사진을 올려 주세요.')
        im = ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((1000, 1000))
        out = io.BytesIO()
        im.save(out, 'JPEG', quality=78)
    return base64.b64encode(out.getvalue()).decode('ascii')


class Store:
    def __init__(self, config):
        self.url = str(config.get('SUPABASE_URL', '')).rstrip('/')
        self.key = str(config.get('SUPABASE_SERVICE_ROLE_KEY', ''))
        if bool(self.url) != bool(self.key):
            raise ValueError('Supabase URL과 서버용 키를 모두 설정해 주세요.')
        self.cloud = bool(self.url and self.key)
        if self.cloud:
            if not self.url.startswith('https://'):
                raise ValueError('Supabase URL은 HTTPS여야 합니다.')
            self.headers = {'apikey': self.key, 'Authorization': f'Bearer {self.key}', 'Content-Type': 'application/json'}
        else:
            Path('data').mkdir(exist_ok=True)
            with sqlite3.connect('data/fridge.db') as con:
                con.execute('CREATE TABLE IF NOT EXISTS fridge_records (id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL)')

    def _request(self, method, **kwargs):
        r = requests.request(method, self.url + '/rest/v1/fridge_records', headers=self.headers, timeout=25, **kwargs)
        r.raise_for_status()
        return r

    def all(self, kind):
        if self.cloud:
            rows, offset = [], 0
            while True:
                batch = self._request('GET', params={'kind': f'eq.{kind}', 'select': 'id,kind,payload', 'order': 'id.asc', 'limit': '100', 'offset': str(offset)}).json()
                rows.extend(batch)
                if len(batch) < 100:
                    break
                offset += len(batch)
            return [dict(row['payload'], id=row['id']) for row in rows]
        with sqlite3.connect('data/fridge.db') as con:
            return [dict(json.loads(row[1]), id=row[0]) for row in con.execute('SELECT id,payload FROM fridge_records WHERE kind=?', (kind,))]

    def put(self, kind, payload, record_id=None):
        rid = record_id or str(uuid.uuid4())
        clean = {k: v for k, v in payload.items() if k != 'id'}
        if self.cloud:
            headers = dict(self.headers, Prefer='resolution=merge-duplicates,return=minimal')
            r = requests.post(self.url + '/rest/v1/fridge_records', headers=headers, params={'on_conflict': 'id'}, json={'id': rid, 'kind': kind, 'payload': clean}, timeout=25)
            r.raise_for_status()
        else:
            with sqlite3.connect('data/fridge.db') as con:
                con.execute('INSERT INTO fridge_records VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET kind=excluded.kind,payload=excluded.payload', (rid, kind, json.dumps(clean, ensure_ascii=False)))
        return rid

    def delete(self, record_id):
        if self.cloud:
            self._request('DELETE', params={'id': f'eq.{record_id}'})
        else:
            with sqlite3.connect('data/fridge.db') as con:
                con.execute('DELETE FROM fridge_records WHERE id=?', (record_id,))

    def consume(self, item, shopping=False):
        # Stable shopping ID makes retries idempotent.
        if shopping:
            sid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'fridge-shopping:' + item['id']))
            self.put('shopping', {'name': item['name'], 'quantity': item.get('quantity', ''), 'checked': False}, sid)
        self.put('item', dict(item, active=False, consumed=datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()), item['id'])

def notification_candidates(items, today):
    return [x for x in items if x.get('active', True) and x.get('expiry') and remaining(x, today) in (1, 0)]


def run_notifications(config):
    """Daily external scheduler entrypoint; never starts a background server."""
    store = Store(config)
    if not store.cloud:
        raise ValueError('Notifications require shared Supabase storage')
    token = str(config.get('TELEGRAM_BOT_TOKEN', ''))
    chats = [x.strip() for x in str(config.get('TELEGRAM_CHAT_IDS', '')).split(',') if x.strip()]
    if not token or not chats:
        raise ValueError('Telegram credentials missing')
    today = datetime.now(ZoneInfo('Asia/Seoul')).date()
    candidates = notification_candidates(store.all('item'), today)
    # Sequential GitHub concurrency group prevents overlapping jobs. Unique ledger key
    # makes ordinary reruns skip delivered notifications. No ambiguous failure retry.
    ledger = {x['id'] for x in store.all('notification')}
    for item in candidates:
        for chat in chats:
            rid = str(uuid.uuid5(uuid.NAMESPACE_URL, f'fridge-alert:{item["id"]}:{item["expiry"]}:{today}:{chat}'))
            if rid in ledger:
                continue
            fresh = next((x for x in store.all('item') if x['id'] == item['id']), None)
            if not fresh or not fresh.get('active', True) or fresh.get('expiry') != item['expiry']:
                continue
            # Reserve before sending: at-most-once attempt, avoiding repeated alerts
            # after a timeout; a failed/uncertain attempt needs manual review.
            store.put('notification', {'status': 'reserved', 'day': today.isoformat(), 'item_id': item['id']}, rid)
            try:
                result = requests.post('https://api.telegram.org/bot' + token + '/sendMessage', json={'chat_id': chat, 'text': '🥬 우리 집 냉장고\n' + item['name'] + '\n' + expiry_label(item, today) + '\n포장지와 보관 상태를 확인하세요. 안전성 판정이 아닙니다.'}, timeout=20)
                result.raise_for_status()
                if not result.json().get('ok'):
                    raise ValueError('Telegram rejected delivery')
                store.put('notification', {'status': 'sent', 'day': today.isoformat(), 'item_id': item['id']}, rid)
            except Exception:
                raise RuntimeError('알림 전송 또는 결과 기록 실패. 중복 방지를 위해 자동 재발송하지 않습니다. notification 기록과 수신 여부를 확인하세요.') from None
    print('Notification run completed')


if __name__ == '__main__' and '--notify' in __import__('sys').argv:
    import os
    try:
        run_notifications({k: os.environ.get(k, '') for k in ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_IDS']})
    except Exception:
        print('알림 실행 실패: 설정/연결과 Supabase notification 기록을 확인하세요. 보안을 위해 원본 오류는 출력하지 않습니다.')
        raise SystemExit(1)
    raise SystemExit(0)

def show_board(active):
    import html
    import re
    try:
        magnets = store.all('magnet')
    except Exception:
        st.error('메모를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.')
        magnets = []
    now = today_korea()
    due = sum(remaining(x, now) == 0 for x in active)
    tomorrow = sum(remaining(x, now) == 1 for x in active)
    notes = [m for m in magnets if m.get('type') == '메모']
    stickers = ''
    mode = st.radio('냉장고 게시판', ['메모', '연락처'], horizontal=True, key='board_mode')
    if st.button('＋ 메모 쓰기' if mode == '메모' else '＋ 연락처 넣기', use_container_width=True, type='primary'):
        add_magnet_dialog(mode)
    visible = [m for m in magnets if m.get('type') == mode]
    if not visible:
        st.info('아직 메모가 없어요. 위 버튼으로 써 보세요.' if mode == '메모' else '아직 연락처가 없어요. 위 버튼으로 넣어 주세요.')
    for m in visible:
        if mode == '메모':
            st.markdown('<div class="board-note">📝 ' + html.escape(m.get('text', '')) + '</div>', unsafe_allow_html=True)
        else:
            phone = re.sub(r'[^0-9+]', '', m.get('phone', ''))
            st.markdown('<div class="phone-magnet">☎ <b>' + html.escape(m.get('text', '')) + '</b> · <a href="tel:' + phone + '">전화하기 ' + html.escape(m.get('phone', '')) + '</a></div>', unsafe_allow_html=True)
        if st.button('내용 수정', key='edit_board_' + m['id'], use_container_width=True):
            edit_magnet_dialog(m)
    st.markdown('<div class="real-appliance"><div class="brand-mark">OUR HOME</div><div class="fridge-seam-v"></div><div class="fridge-seam-h"></div><div class="handle handle-left"></div><div class="handle handle-right"></div><div class="black-display"><small>우리 집 냉장고</small><p>오늘까지 <b>' + str(due) + '</b>개</p><p>내일까지 <b>' + str(tomorrow) + '</b>개</p><small>보관 중 ' + str(len(active)) + '개</small></div>' + stickers + '<div class="bottom-grill"></div></div>', unsafe_allow_html=True)
    if st.button('🚪 냉장고 문 열기', type='primary', use_container_width=True):
        st.session_state.opened = True
        st.rerun()
    with st.expander('🔔 먼저 먹을 음식 확인'):
        soon = sorted([x for x in active if remaining(x, now) is not None and remaining(x, now) <= 1], key=lambda x: urgency(x, now))
        if not soon:
            st.write('오늘·내일 기한인 음식이 없어요.')
        for item in soon:
            if st.button(item['name'] + ' · ' + expiry_label(item, now), key='jump_' + item['id'], use_container_width=True):
                st.session_state.opened = True
                st.session_state.room_choice = item.get('room', '냉장실')
                st.session_state.current_zone = item.get('zone', '상단 선반')
                st.rerun()


import hmac
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
import qrcode
import streamlit as st


def today_korea():
    return datetime.now(ZoneInfo('Asia/Seoul')).date()


def calendar_bytes(items, alarm_time=None):
    alarm_time = alarm_time or __import__("datetime").time(20, 0)
    def esc(s):
        return str(s).replace('\\', '\\\\').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Our Fridge//Expiry reminders//KO', 'CALSCALE:GREGORIAN', 'BEGIN:VTIMEZONE', 'TZID:Asia/Seoul', 'BEGIN:STANDARD', 'DTSTART:19700101T000000', 'TZOFFSETFROM:+0900', 'TZOFFSETTO:+0900', 'TZNAME:KST', 'END:STANDARD', 'END:VTIMEZONE']
    for item in items:
        if not item.get('expiry'):
            continue
        day = date.fromisoformat(item['expiry'])
        lines.extend(['BEGIN:VEVENT', f'UID:{item["id"]}@our-fridge', 'DTSTAMP:' + datetime.now(ZoneInfo('UTC')).strftime('%Y%m%dT%H%M%SZ'), 'DTSTART;TZID=Asia/Seoul:' + day.strftime('%Y%m%d') + alarm_time.strftime('T%H%M%S'), 'DTEND;TZID=Asia/Seoul:' + (datetime.combine(day, alarm_time) + timedelta(minutes=10)).strftime('%Y%m%dT%H%M%S'), 'SUMMARY:' + esc('오늘 ' + item['name'] + ' ' + item.get('date_type', '소비기한') + '이에요'), 'DESCRIPTION:' + esc('포장지 표시 기한을 확인하세요. 안전성 판정이 아닙니다. 앱 변경/소진은 이 일정을 자동 변경하지 않습니다.')])
        for trigger in ['-P1D', 'PT0M']:
            lines.extend(['BEGIN:VALARM', 'ACTION:DISPLAY', 'TRIGGER:' + trigger, 'DESCRIPTION:' + esc(item['name'] + ' 표시 기한 확인'), 'END:VALARM'])
        lines.append('END:VEVENT')
    lines.append('END:VCALENDAR')
    # RFC 5545: fold by UTF-8 octets without splitting characters.
    folded = []
    for line in lines:
        part = ''
        for ch in line:
            if len((part + ch).encode('utf-8')) > 74:
                folded.append(part)
                part = ' ' + ch
            else:
                part += ch
        folded.append(part)
    return ('\r\n'.join(folded) + '\r\n').encode('utf-8')


st.set_page_config(page_title='우리 집 냉장고', page_icon='🥬', layout='centered')
st.markdown('''<style>
.stApp{background:#faf7ef;color:#213c33}.block-container{max-width:850px;padding-top:1.5rem}
h1,h2,h3{color:#213c33}.stButton>button{min-height:48px;border-radius:14px;border-color:#b4c8bb}
.stButton>button[kind="primary"]{background:#2f6951;color:white;border-color:#2f6951}
.door{background:linear-gradient(120deg,#fffdf5,#eee7d5,#fffaf0);border:2px solid #aebfc4;border-radius:22px;padding:26px 25px 26px 48px;position:relative;margin:8px 0;color:#213c33}
.door:before{content:"";position:absolute;left:18px;top:25px;bottom:25px;width:9px;border-radius:9px;background:linear-gradient(90deg,#859ba3,#fff,#80969e)}
.door strong{font-size:24px}.door p{color:#425b61}
.magnet{border-radius:5px 5px 15px 5px;padding:12px 18px 18px;margin:12px 0;min-height:110px;box-shadow:2px 5px 9px #54462b18;overflow-wrap:anywhere;color:#293f35}.magnet p{white-space:pre-wrap}.magnet a{color:#234c3b;font-weight:700}.pin{display:block;text-align:center;color:#b46f60;font-size:22px;text-shadow:1px 2px 2px #5432}
@media(max-width:600px){.block-container{padding:1rem}}

/* Appliance shell: Streamlit's keyed containers keep real controls inside doors. */
.st-key-fridge_front{max-width:570px;margin:18px auto 38px;padding:24px 24px 52px!important;border:3px solid #c7c3b7;border-radius:29px 29px 19px 19px;background:linear-gradient(100deg,#ddd9cc 0%,#fffdf4 8%,#f5f1e6 65%,#e5e0d3 96%,#c4c0b5 100%);box-shadow:inset 2px 0 3px #fff, inset -4px 0 6px #9b968b55,12px 16px 28px #423e2929;position:relative;isolation:isolate}
.st-key-fridge_front:before{content:"";position:absolute;left:20px;right:20px;bottom:15px;height:17px;border-radius:4px;background:repeating-linear-gradient(0deg,#696b64 0px,#696b64 2px,#b7b6ab 2px,#b7b6ab 5px);box-shadow:0 2px 2px #fff}
.st-key-fridge_front:after{content:"";position:absolute;bottom:-9px;left:38px;right:38px;height:9px;border-left:23px solid #56594e;border-right:23px solid #56594e;z-index:-1}
.st-key-fridge_front .door{margin:0 0 14px;padding:24px 20px 30px 55px;min-height:175px;border:1px solid #d6d0c1;border-bottom:5px solid #a5a399;border-radius:17px 17px 5px 5px;background:linear-gradient(110deg,#fffdf6,#f0ecdf);box-shadow:inset 0 2px 2px #fff,0 3px 2px #78776d33}
.st-key-fridge_front .door:before{left:19px;top:46px;bottom:27px;width:13px;background:linear-gradient(90deg,#92978f,#fdfdfa 48%,#b6bbb1 80%,#848a80);box-shadow:3px 3px 4px #62695c55}
.st-key-fridge_front .door:after{content:"FREEZER  −18°C";position:absolute;right:16px;top:12px;font-size:10px;letter-spacing:1.6px;color:#758071}
.st-key-fridge_front .magnet{margin:9px 1px 3px;box-shadow:2px 5px 6px #69614c30;transform:rotate(-1deg);border-top:1px solid #ffffff88}
.st-key-fridge_front [data-testid="stColumn"]:nth-child(2) .magnet{transform:rotate(1.5deg)}
.st-key-fridge_inside{max-width:650px;margin:16px auto;padding:22px!important;border:12px solid #e1ded2;border-radius:24px;background:linear-gradient(90deg,#d9e5e4,#f7fcfa 12%,#eef7f5 88%,#cbdcdb);box-shadow:inset 0 0 14px #899f9d88,7px 12px 22px #414b3c22;position:relative}
.st-key-fridge_inside:before{content:"";display:block;height:8px;width:46%;margin:0 auto 14px;background:#fffde1;border-radius:6px;box-shadow:0 0 18px 6px #fffce8}
.st-key-fridge_inside [data-testid="stVerticalBlockBorderWrapper"]{background:#ffffff70;border-bottom:5px solid #adc5c2!important;border-radius:9px!important;box-shadow:0 5px 0 #ffffffb0,0 8px 8px #758e8930;margin-bottom:12px}
.appliance-label{text-align:center;font-size:11px;letter-spacing:3px;color:#7c8174;padding:8px 0 15px;border-top:2px solid #d8d3c5;margin-top:8px}
@media(max-width:600px){.st-key-fridge_front{padding:15px 13px 45px!important}.st-key-fridge_inside{padding:12px!important;border-width:8px}.st-key-fridge_front .door strong{font-size:21px}}

/* Game-like shelf inventory: real Streamlit buttons, no click-through image hacks. */
[class*="st-key-shelf_"]{padding:12px 8px 20px!important;margin:6px 0 20px;background:linear-gradient(180deg,#e6f1ee,#f5faf7 85%,#c5d7d2);border-bottom:8px solid #94b8b2;border-radius:6px;box-shadow:0 5px 0 #e6f4ef,0 9px 7px #597c7138}
[class*="st-key-shelf_"][class*="채소칸"]{border:3px solid #adc8b5;border-bottom-width:9px;border-radius:6px 6px 22px 22px;background:#dfeddca0}
.food-object{min-height:175px;padding:10px 3px 5px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;text-align:center}
.food-object img{width:90px;height:105px;object-fit:cover;border-radius:15px 15px 8px 8px;border:3px solid #fffdf6;box-shadow:4px 7px 5px #3d5e472e;transform:rotate(-2deg)}
.food-object .food-emoji{font-size:65px;line-height:110px;filter:drop-shadow(4px 7px 3px #3d5e4733)}
.food-label{font-size:14px;font-weight:750;margin:9px 0 4px;overflow-wrap:anywhere}.food-object small{font-size:11px;border-radius:8px;padding:3px 5px;color:#294239}
@media(max-width:600px){.food-object img{width:65px;height:85px}.food-object{min-height:150px}.food-object .food-emoji{font-size:48px;line-height:85px}}

/* Easy-use two-door appliance, generous typography and stable two-up mobile grid. */
.st-key-fridge_front{background:linear-gradient(90deg,#dedbd2 0%,#faf9f0 5%,#f1eee4 49.3%,#7f867e 49.7%,#515d55 50%,#b4b9ae 50.4%,#fffdf4 51%,#eeeadd 96%,#c9c8bc 100%);border-radius:25px 25px 14px 14px;min-height:530px}
.st-key-fridge_front .door{min-height:215px;border:0;border-bottom:0;background:transparent;box-shadow:none;padding:44px 12px 40px;text-align:center;position:relative}
.st-key-fridge_front .door:before{left:calc(50% - 23px);top:116px;bottom:12px;width:11px;border-radius:8px;background:linear-gradient(90deg,#a3aaa1,#fff,#818b80);box-shadow:2px 3px 4px #30413255}
.st-key-fridge_front .door:after{content:"";position:absolute;left:calc(50% + 13px);top:116px;bottom:12px;width:11px;border-radius:8px;background:linear-gradient(90deg,#a3aaa1,#fff,#818b80);box-shadow:2px 3px 4px #30413255}
.st-key-fridge_front .door small{letter-spacing:2px;font-size:10px}.st-key-fridge_front .door span{font-size:13px;background:#faf7ecdd;padding:4px 9px;border-radius:8px}
.stButton>button,.stDownloadButton>button{min-height:52px!important;font-size:17px!important;font-weight:650;border-radius:13px}
[data-testid="stWidgetLabel"] p{font-size:17px}.food-label{font-size:19px}.food-object small{font-size:14px;padding:5px 8px}.food-object img{width:112px;height:120px}.food-object{min-height:200px}
@media(max-width:640px){
[class*="st-key-shelf_"] [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:10px!important}
[class*="st-key-shelf_"] [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{min-width:0!important;width:calc(50% - 5px)!important;flex:1 1 0!important}
.food-object img{width:88px;height:105px}.food-label{font-size:17px}.food-object small{font-size:12px}.food-object{min-height:180px}
.st-key-fridge_inside{padding:9px!important;border-width:6px}.stButton>button p{font-size:15px!important}
}
.neutral-food{display:flex;align-items:center;justify-content:center;width:90px;height:105px;background:#e8e9df;border-radius:12px;color:#66705e;font-size:13px}

/* Reference-inspired dark metal four-door refrigerator; no product photo required. */
.st-key-fridge_front{background:linear-gradient(105deg,#202328 0%,#55585c 18%,#303337 48%,#171a1e 50%,#4b4f53 78%,#24272b 100%)!important;border:5px solid #25282d!important;border-radius:10px!important;box-shadow:14px 20px 22px #0005,inset 4px 0 8px #ffffff40!important;padding:28px 26px 65px!important;position:relative;min-height:620px}
.st-key-fridge_front:before{content:"";position:absolute;left:49.5%;top:0;bottom:15px;width:5px;background:#111;box-shadow:2px 0 2px #ffffff35;pointer-events:none}
.st-key-fridge_front:after{content:"";position:absolute;left:2%;right:2%;top:56%;height:5px;background:#101215;box-shadow:0 3px 2px #ffffff30;pointer-events:none}
.st-key-fridge_front .door{background:linear-gradient(110deg,#55595f,#2c3035)!important;border:1px solid #73777a!important;color:#fff!important;box-shadow:inset 0 1px 2px #fff3!important}
.st-key-fridge_front .door:before{content:"";position:absolute;right:15px;top:22px;width:9px;height:110px;background:linear-gradient(90deg,#17191c,#c2c5c8,#555a60);border-radius:3px;box-shadow:3px 2px 4px #0008}
.st-key-fridge_front .door span,.st-key-fridge_front .door small{color:#e2e6e9!important}
.appliance-label{color:#e4e6e8!important;letter-spacing:2px}
.st-key-fridge_inside{background:linear-gradient(90deg,#bdc2c6,#f1f5f5 8%,#fafcfc 50%,#e4e9ea 93%,#a5acb2)!important;border:12px solid #34393f!important;border-radius:12px!important;box-shadow:inset 0 0 20px #637a8b55,10px 12px 20px #0003!important}
.food-object{min-height:86px!important;justify-content:center!important;background:#fffdf7;border:1px solid #ccd3d2;border-radius:12px;padding:14px 8px!important;box-shadow:0 4px 0 #bcc7c7}
.food-label{font-size:23px!important;line-height:1.5}.food-object small{font-size:17px!important}
button p{font-size:18px!important}input{font-size:19px!important}

.st-key-fridge_front{background:transparent!important;border:0!important;box-shadow:none!important;padding:0!important;min-height:0!important;max-width:520px!important}
.st-key-fridge_front:before,.st-key-fridge_front:after{display:none!important}
.appliance-label{display:none}
.real-appliance{position:relative;width:100%;height:640px;border-radius:10px 10px 5px 5px;border:5px solid #24262a;background:repeating-linear-gradient(91deg,#ffffff02 0px,#ffffff02 1px,#00000002 2px,#00000002 3px),linear-gradient(100deg,#25272a,#55585b 20%,#36393c 47%,#292c2f 52%,#494c50 80%,#292c30);box-shadow:12px 14px 18px #0003,inset 2px 0 5px #ffffff45;margin:12px auto 25px;overflow:hidden}
.brand-mark{position:absolute;top:22px;left:22px;letter-spacing:3px;font-size:11px;color:#e7e9e9}
.fridge-seam-v{position:absolute;top:0;bottom:8px;left:49.6%;width:5px;background:#121416;box-shadow:2px 0 2px #ffffff30}
.fridge-seam-h{position:absolute;top:62%;left:0;right:0;height:7px;background:#111416;box-shadow:0 2px 2px #ffffff35}
.handle{position:absolute;top:28%;height:26%;width:9px;border-radius:3px;background:linear-gradient(90deg,#5e656a,#e5e8eb 45%,#8b949b);box-shadow:3px 2px 5px #0009}
.handle-left{left:45%}.handle-right{left:53%}
.black-display{position:absolute;right:7%;top:10%;width:32%;height:210px;border:2px solid #101215;border-radius:4px;background:linear-gradient(115deg,#13171b,#242c32);box-shadow:inset 0 0 8px #000,1px 1px 2px #ffffff40;color:#eaf5f2;padding:14px 10px}
.black-display small{font-size:12px;color:#a6bfbd}.black-display p{font-size:16px!important;margin:16px 0!important}.black-display b{font-size:25px;color:#b5e6d9}
.paper-note{position:absolute;left:6%;width:32%;padding:10px 12px 17px;background:#fff0b7;color:#3b382b;box-shadow:3px 5px 5px #0005;white-space:pre-wrap;overflow-wrap:anywhere;font-size:16px;max-height:140px;overflow:hidden;line-height:1.45}
.paper-0{top:12%;transform:rotate(-4deg)}.paper-1{top:37%;transform:rotate(3deg);background:#e1ebcf}
.bottom-grill{position:absolute;bottom:8px;left:4%;right:4%;height:9px;background:repeating-linear-gradient(90deg,#121415 0px,#121415 3px,#44484b 3px,#44484b 6px)}
.phone-magnet{background:#f8e7cf;border:1px solid #d9c5a9;border-radius:10px;padding:12px;margin:8px 0;font-size:18px}.phone-magnet a{color:#145242;font-weight:bold}
@media(max-width:480px){.real-appliance{height:530px}.black-display{height:185px;padding:9px}.black-display p{font-size:14px!important}.black-display b{font-size:22px}.paper-note{font-size:15px;padding:8px;max-height:120px}}
.board-note{background:#fff0bc;border-left:6px solid #d0aa40;border-radius:10px;padding:18px;font-size:21px;white-space:pre-wrap;overflow-wrap:anywhere;margin:10px 0}
</style>''', unsafe_allow_html=True)
try:
    config = dict(st.secrets)
except FileNotFoundError:
    config = {}
if 'alarm_time' not in st.session_state:
    try:
        hh, mm = str(config.get('CALENDAR_TIME', '20:00')).split(':')
        st.session_state.alarm_time = __import__('datetime').time(int(hh), int(mm))
    except (ValueError, TypeError):
        st.session_state.alarm_time = __import__('datetime').time(20, 0)
password = str(config.get('APP_PASSWORD', ''))
cloud = bool(config.get('SUPABASE_URL') or config.get('SUPABASE_SERVICE_ROLE_KEY'))
if cloud and len(password) < 10:
    st.error('가족 공유 모드에는 Secrets의 APP_PASSWORD를 10자 이상으로 설정해야 합니다.')
    st.stop()
if password and not st.session_state.get('auth'):
    st.title('🥬 우리 집 냉장고')
    with st.form('login'):
        pw = st.text_input('가족 비밀번호', type='password')
        if st.form_submit_button('열기', type='primary'):
            if hmac.compare_digest(pw.encode(), password.encode()):
                st.session_state.auth = True
                st.rerun()
            st.error('비밀번호를 확인해 주세요.')
    st.stop()
try:
    store = Store(config)
    items = store.all('item')
except Exception:
    st.error('저장소 연결 실패: 앱 파일 상단 안내의 Supabase SQL과 Secrets를 확인하세요.')
    st.stop()


def write_record(kind, payload, rid=None):
    try:
        store.put(kind, payload, rid)
        st.session_state.flash = '저장했어요!'
        st.rerun()
    except Exception:
        st.error('저장하지 못했습니다. 연결을 확인하고 다시 시도해 주세요.')


def delete_record(rid):
    try:
        store.delete(rid)
        st.rerun()
    except Exception:
        st.error('삭제하지 못했습니다. 다시 시도해 주세요.')


@st.dialog('메모·연락처 수정')
def edit_magnet_dialog(record):
    import re
    with st.form('edit_board_dialog'):
        text = st.text_area('메모 내용' if record.get('type') == '메모' else '가게 이름', value=record.get('text', ''), max_chars=150)
        phone = st.text_input('전화번호', value=record.get('phone', ''), max_chars=30) if record.get('type') == '연락처' else ''
        if st.form_submit_button('저장', type='primary', use_container_width=True):
            if not text.strip():
                st.error('내용을 적어 주세요.')
            elif record.get('type') == '연락처' and not re.fullmatch(r'[0-9+()\-\s]{3,30}', phone.strip()):
                st.error('전화번호를 확인해 주세요.')
            else:
                write_record('magnet', dict(record, text=text.strip(), phone=phone.strip()), record['id'])
    confirm = st.checkbox('이 내용을 지울게요', key='confirm_edit_delete')
    if st.button('지우기', disabled=not confirm, use_container_width=True):
        delete_record(record['id'])


@st.dialog('냉장고에 붙이기')
def add_magnet_dialog(kind):
    import re
    with st.form('new_magnet_dialog'):
        text = st.text_area('메모 내용' if kind == '메모' else '가게 이름', max_chars=150)
        phone = st.text_input('전화번호', placeholder='예: 02-123-4567', max_chars=30) if kind == '연락처' else ''
        if st.form_submit_button('붙이기', type='primary', use_container_width=True):
            if not text.strip():
                st.error('내용을 적어 주세요.')
            elif kind == '연락처' and not re.fullmatch(r'[0-9+()\-\s]{3,30}', phone.strip()):
                st.error('전화번호를 확인해 주세요.')
            else:
                write_record('magnet', dict(type=kind, text=text.strip(), phone=phone.strip()))


def register_form(room, zone, item=None):
    old = item or {}
    key = old.get('id', 'new_' + room + '_' + zone + '_' + str(st.session_state.get('register_revision', 0)))
    with st.form('food_' + key, clear_on_submit=not bool(item)):
        name = st.text_input('음식 이름 *', value=old.get('name', ''), placeholder='예: 우유', max_chars=60)
        expiry = st.date_input('소비기한 · 모르면 비워 두세요', value=date.fromisoformat(old['expiry']) if old.get('expiry') else None, key='date_' + key, min_value=min(today_korea(), date.fromisoformat(old['expiry'])) if old.get('expiry') else today_korea())
        st.caption('기본: 구매일 오늘 · 지금 선택한 칸에 보관. 다른 정보는 입력하지 않아도 됩니다.')
        if item:
            purchase = st.date_input('구매일', value=date.fromisoformat(old['purchase']) if old.get('purchase') else today_korea(), max_value=today_korea())
            types = ['소비기한', '유통기한', '품질유지기한']
            dtype = st.selectbox('위 날짜의 종류', types, index=types.index(old.get('date_type', '소비기한')))
            locs = [f'{r} / {z}' for r, zs in ZONES.items() for z in zs]
            current = f'{old.get("room", room)} / {old.get("zone", zone)}'
            location = st.selectbox('보관 칸', locs, index=locs.index(current) if current in locs else 0)
            state = st.selectbox('직접 확인한 상태', STATES, index=STATES.index(old.get('state', '확인 필요')))
        else:
            purchase = today_korea()
            dtype = '소비기한'
            location = f'{room} / {zone}'
            state = '확인 필요'
        submitted = st.form_submit_button('저장', type='primary', use_container_width=True)
    if submitted:
        if not name.strip():
            st.error('이름만 입력하면 저장할 수 있어요.')
            return
        if expiry and expiry < today_korea() and (not old.get('expiry') or expiry.isoformat() != old['expiry']):
            st.error('새 기한은 오늘 이후 날짜로 선택해 주세요. 기존의 지난 기한은 그대로 보존할 수 있어요.')
            return
        r, z = location.split(' / ')
        # Do not silently refresh the last state check when only editing another field.
        checked_at = old.get('checked_at')
        if state != old.get('state', '확인 필요') or (not item and state != '확인 필요'):
            checked_at = today_korea().isoformat()
        payload = dict(old, name=name.strip(), photo=None, purchase=purchase.isoformat(), expiry=expiry.isoformat() if expiry else None, date_type=dtype, room=r, zone=z, state=state, checked_at=checked_at, active=True)
        try:
            saved_id = store.put('item', payload, old.get('id'))
        except Exception:
            st.error('저장하지 못했습니다. 연결을 확인하고 다시 시도해 주세요.')
            return
        if payload.get('expiry'):
            st.session_state.calendar_saved = dict(payload, id=saved_id)
        else:
            st.session_state.pop('calendar_saved', None)
        st.session_state.register_revision = st.session_state.get('register_revision', 0) + 1
        st.session_state.flash = '저장했어요!'
        st.rerun()


def food_icon(name):
    for words, icon in [('우유 요거트 치즈', '🥛'), ('계란 달걀', '🥚'), ('당근', '🥕'), ('상추 배추 시금치 채소', '🥬'), ('사과', '🍎'), ('바나나', '🍌'), ('고기 소고기 돼지', '🥩'), ('닭 치킨', '🍗'), ('물 음료 주스', '🧃'), ('생선', '🐟')]:
        if any(word in name for word in words.split()):
            return icon
    return '🥗'


@st.dialog('＋ 음식 넣기', width='large')
def add_food_dialog(room, zone):
    st.caption(room + ' / ' + zone + '에 넣어요. 이름만 적어도 저장됩니다.')
    register_form(room, zone)


@st.dialog('냉장고 속 재료', width='large')
def food_details(food):
    st.subheader(food['name'])
    st.write(expiry_label(food, today_korea()))
    st.caption('구매일 ' + food.get('purchase', '미입력') + ' · ' + food.get('room', '') + ' / ' + food.get('zone', ''))
    st.caption('직접 기록한 상태: ' + food.get('state', '확인 필요'))
    if st.button('✓ 다 먹었어요', key='detail_eat_' + food['id'], type='primary', use_container_width=True):
        try:
            store.consume(food)
        except Exception:
            st.error('소진 처리 실패. 다시 시도해 주세요.')
            return
        st.session_state.just_consumed = food
        st.rerun()
    if food.get('expiry'):
        calendar_action(food, 'detail_calendar_' + food['id'])
        st.caption('날짜 변경·소진·삭제 시 기존 캘린더 일정은 직접 수정/삭제하세요.')
    with st.expander('자세히 수정'):
        register_form(food.get('room', '냉장실'), food.get('zone', '상단 선반'), food)
    with st.expander('삭제'):
        confirm = st.checkbox('이 재료를 영구 삭제합니다', key='remove_confirm_' + food['id'])
        if st.button('영구 삭제', disabled=not confirm, key='remove_' + food['id']):
            delete_record(food['id'])


st.title('🥬 우리 집 냉장고')
st.caption('사진 넣고, 이름 적고, 저장. 소비기한은 알 때만 넣어 주세요.')
if not store.cloud:
    st.warning('로컬 체험 모드 · 가족 공유/재시작 후 데이터 유지에는 Supabase 설정이 필요합니다.')
if st.session_state.get('flash'):
    st.toast(st.session_state.pop('flash'))

def calendar_action(food, key):
    st.download_button('🔔 캘린더에 알림 추가', calendar_bytes([food], st.session_state.get('alarm_time')),
                       file_name='fridge-' + food['id'] + '.ics', mime='text/calendar',
                       key=key, use_container_width=True)
    st.caption('알림 시각: ' + st.session_state.get('alarm_time', __import__('datetime').time(20, 0)).strftime('%H:%M') + ' · 설정 / QR에서 변경')
    st.caption('① 버튼 누르기 → ② 받은 일정을 휴대폰 캘린더에서 열고 추가 → ③ 알림 확인. 하루 전·당일 선택한 시간(한국 시간) 알림을 요청합니다.')
    st.caption('기기에 따라 파일을 직접 열어야 하거나 PC 캘린더에서 가져와야 합니다. 다운로드만으로 알림이 켜지지는 않으며 캘린더 앱의 알림 권한이 필요합니다.')

active = [x for x in items if x.get('active', True)]
if st.session_state.get('calendar_saved'):
    saved = st.session_state.calendar_saved
    current_saved = next((x for x in active if x['id'] == saved['id']), None)
    if current_saved and current_saved.get('expiry'):
        with st.container(border=True):
            st.success(current_saved['name'] + ' 저장 완료! 휴대폰 알림도 추가해 보세요.')
            calendar_action(current_saved, 'just_saved_calendar')
            st.caption('앱에서 날짜를 바꾸거나 다 먹어도 캘린더는 자동 변경되지 않습니다. 이전 일정을 수정·삭제하세요. 같은 일정을 반복 추가하지 마세요.')
            if st.button('확인했어요', key='close_calendar_saved'):
                st.session_state.pop('calendar_saved', None)
                st.rerun()

today = today_korea()
view = st.radio('메뉴', ['냉장고', '장보기', '설정 / QR'], horizontal=True, label_visibility='collapsed')

# Notifications are refreshed while the page is open. No background push is claimed.
@st.fragment(run_every='60s')
def expiry_notices():
    try:
        fresh = [x for x in store.all('item') if x.get('active', True)]
    except Exception:
        st.warning('기한 알림을 새로 불러오지 못했습니다. 잠시 후 다시 확인하세요.')
        return
    now = today_korea()
    alerts = [x for x in fresh if remaining(x, now) is not None and remaining(x, now) <= 1]
    if alerts:
        st.warning('🔔 기한 확인: ' + ' / '.join(f'{x["name"]} · {expiry_label(x, now)}' for x in sorted(alerts, key=lambda x: urgency(x, now))))
        token = (now.isoformat(), tuple((x['id'], x.get('expiry')) for x in sorted(alerts, key=lambda x: x['id'])))
        if st.session_state.get('alert_token') != token:
            st.toast('🔔 표시 기한이 가깝거나 지난 식재료가 있어요.')
            st.session_state.alert_token = token
    st.caption('앱을 열어 둔 동안 1분마다 알림을 확인합니다. 표시 기한은 음식의 부패나 섭취 안전성을 판정하지 않습니다.')
expiry_notices()

if view == '냉장고':
    if not st.session_state.get('opened'):
        with st.container(key='fridge_front'):
            show_board(active)
            st.markdown('<div class="appliance-label">FRESH HOME · REFRIGERATOR</div>', unsafe_allow_html=True)
    else:
        with st.container(key='fridge_inside'):
            if st.button('← 문 닫기'):
                st.session_state.opened = False
                st.rerun()
            if st.session_state.pop('clear_find', False):
                st.session_state.find_food = ''
            query = st.text_input('음식 찾기', placeholder='예: 우유', key='find_food')
            if query.strip():
                found = [f for f in active if query.strip().casefold() in f['name'].casefold()]
                if not found:
                    st.info('찾는 음식이 없어요.')
                for food in found:
                    st.write('**' + food['name'] + '** · ' + food.get('room', '') + ' / ' + food.get('zone', ''))
                    if st.button('이 칸 보기', key='find_' + food['id']):
                        st.session_state.room_choice = food.get('room', '냉장실')
                        st.session_state.current_zone = food.get('zone', '상단 선반')
                        st.session_state.clear_find = True
                        st.rerun()
            room = st.radio('어디를 볼까요?', list(ZONES), horizontal=True, key='room_choice')
            zones = ZONES[room]
            if st.session_state.get('current_zone') not in zones:
                st.session_state.current_zone = zones[0]
            st.caption('음식을 넣을 칸을 골라 주세요. 선택한 칸의 음식만 아래에 보여요.')
            cols = st.columns(2)
            for idx, z in enumerate(zones):
                with cols[idx % 2]:
                    count = sum(x.get('room') == room and x.get('zone') == z for x in active)
                    if st.button(f'{"🥬" if z == "채소칸" else "🥛" if z == "문쪽 수납칸" else "🧊"} {z} · {count}', key='zone_' + z, type='primary' if st.session_state.current_zone == z else 'secondary', use_container_width=True):
                        st.session_state.current_zone = z
                        st.session_state.all_food = False
                        st.session_state.pop('focus_item', None)
                        st.rerun()
            zone = st.session_state.current_zone
            if st.button('＋ 음식 넣기', type='primary', use_container_width=True):
                add_food_dialog(room, zone)
            st.subheader('📍 ' + room + ' · ' + zone)
            st.caption('위에서 다른 칸을 누르면 이곳의 음식이 바뀝니다.')
            if st.session_state.get('focus_item'):
                st.info('선택한 재료는 아래 이름 버튼으로 상세 확인할 수 있어요.')
                st.session_state.pop('focus_item', None)
            if not active:
                st.info('아직 빈 냉장고예요. 위에서 식재료를 넣어 보세요.')
            for shelf_room, shelf_zones in [(room, [zone])]:
                st.subheader(('🧊 ' if shelf_room == '냉동실' else '🧺 ' if shelf_room == '실온' else '❄️ ') + shelf_room)
                for shelf_zone in shelf_zones:
                    shelf_items = sorted([x for x in active if x.get('room') == shelf_room and x.get('zone') == shelf_zone], key=lambda x: urgency(x, today))
                    if not shelf_items:
                        st.info('이 칸은 비어 있어요. ＋ 음식 넣기를 눌러 주세요.')
                        continue
                    with st.container(key='shelf_' + shelf_room + '_' + shelf_zone):
                        st.markdown('**' + shelf_zone + '** · ' + str(len(shelf_items)))
                        if not shelf_items:
                            st.caption('빈자리 · 새로운 재료를 기다리고 있어요')
                        for offset in range(0, len(shelf_items), 1):
                            spots = st.columns(1)
                            for col, food in zip(spots, shelf_items[offset:offset+1]):
                                with col:
                                    import html
                                    rid = food['id']
                                    days = remaining(food, today)
                                    badge = '#edb4a8' if days is not None and days < 0 else '#f3d789' if days is not None and days <= 1 else '#d0e2c4'
                                    picture = ""
                                    st.markdown('<div class="food-object">' + picture + '<div class="food-label">' + html.escape(food['name']) + '</div><small style="background:' + badge + '">' + html.escape(expiry_label(food, today)) + '</small></div>', unsafe_allow_html=True)
                                    if st.button('자세히 보기', key='pick_' + rid, use_container_width=True):
                                        food_details(food)
                                    if st.button('✓ 다 먹었어요', key='quick_eat_' + rid, use_container_width=True):
                                        try:
                                            store.consume(food)
                                        except Exception:
                                            st.error('저장하지 못했어요. 다시 눌러 주세요.')
                                        else:
                                            st.session_state.just_consumed = food
                                            st.rerun()
            # Preserve any old records with nonstandard locations rather than hiding them.
            unknown = [x for x in active if x.get('zone') not in ZONES.get(x.get('room'), [])]
            if unknown:
                st.subheader('📦 위치 확인이 필요한 재료')
                for food in unknown:
                    if st.button(food['name'] + ' · 위치 수정', key='unknown_' + food['id']):
                        food_details(food)
            if st.session_state.get('just_consumed'):
                last = st.session_state.just_consumed
                with st.container(border=True):
                    st.write(f'✓ {last["name"]} 소진 처리했어요.')
                    st.caption('이 재료를 캘린더에 추가했다면 해당 일정도 직접 삭제해 주세요.')
                    a, b, c = st.columns(3)
                    if a.button('장보기에 추가'):
                        sid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'fridge-shopping:' + last['id']))
                        try:
                            store.put('shopping', {'name': last['name'], 'checked': False}, sid)
                            del st.session_state.just_consumed
                            st.rerun()
                        except Exception:
                            st.error('추가 실패. 다시 시도해 주세요.')
                    if b.button('되돌리기'):
                        del st.session_state.just_consumed
                        write_record('item', dict(last, active=True, consumed=None), last['id'])
                    if c.button('닫기'):
                        del st.session_state.just_consumed
                        st.rerun()

elif view == '장보기':
    with st.form('shop', clear_on_submit=True):
        name = st.text_input('살 물건 이름', max_chars=60)
        if st.form_submit_button('추가') and name.strip():
            write_record('shopping', {'name': name.strip(), 'checked': False})
    try:
        rows = store.all('shopping')
    except Exception:
        st.error('장보기 목록을 불러오지 못했습니다.')
        st.stop()
    pending = [row for row in rows if not row.get('checked', False)]
    if st.session_state.get('last_checked_shop'):
        last = st.session_state.last_checked_shop
        st.success(last['name'] + ' 구매 완료!')
        if st.button('↩ 잘못 체크했어요 · 되돌리기', use_container_width=True):
            try:
                store.put('shopping', dict(last, checked=False), last['id'])
            except Exception:
                st.error('되돌리지 못했어요. 다시 눌러 주세요.')
            else:
                st.session_state.pop('last_checked_shop', None)
                st.session_state.pop('check_' + last['id'], None)
                st.rerun()
    if not pending:
        st.info('살 물건이 없어요. 필요한 물건을 위에 적어 주세요.')
    for row in pending:
        a, b = st.columns([4, 1])
        checked = a.checkbox(row['name'], value=False, key='check_' + row['id'])
        if checked:
            try:
                store.put('shopping', dict(row, checked=True), row['id'])
            except Exception:
                st.error('저장하지 못했어요. 다시 시도해 주세요.')
            else:
                st.session_state.last_checked_shop = row
                st.rerun()
        if b.button('지우기', key='shopdel_' + row['id']):
            st.session_state.last_checked_shop = row
            write_record('shopping', dict(row, checked=True), row['id'])

else:
    st.subheader('알림 설정')
    st.time_input('🔔 캘린더 알림 받을 시간', key='alarm_time', step=300)
    st.caption('하루 전과 당일에 이 시각으로 알림을 요청합니다. 기본은 저녁 8시. 이미 추가한 캘린더 일정은 자동 변경되지 않습니다. 재접속 기본값을 바꾸려면 Secrets에 CALENDAR_TIME = "20:00"처럼 설정하세요.')
    st.info('아래 버튼으로 받은 일정 파일을 휴대폰 캘린더에 추가해 주세요. 다운로드만으로 알림이 켜지지는 않습니다.')
    st.write('앱 안 알림: 표시 기한 하루 전부터, 당일과 지난 기한을 함께 표시합니다.')
    st.write('앱 밖 알림: 아래 파일을 휴대폰 캘린더에 가져오면 하루 전·당일 선택한 시간(한국 시간) 알림을 요청합니다.')
    eligible = [x for x in active if x.get('expiry') and date.fromisoformat(x['expiry']) >= today]
    if eligible:
        st.download_button('📅 모든 재료 캘린더 알림 받기', calendar_bytes(eligible, st.session_state.get('alarm_time')), file_name='fridge-reminders.ics', mime='text/calendar')
    else:
        st.info('오늘 이후 표시 기한이 있는 재료를 등록하면 캘린더 파일을 받을 수 있어요.')
    st.caption('자동 푸시 기능은 아닙니다. 다운로드만으로 알림이 설정되지는 않습니다. 파일을 캘린더에 가져온 뒤 알림 권한과 일정을 확인하세요. 일부 캘린더는 파일의 알림을 무시하므로 일정에서 직접 알림을 설정해야 합니다. 선택한 시간이 지난 당일이나 이미 지난 알림은 울리지 않을 수 있습니다. 앱의 변경/소진/삭제는 캘린더에 반영되지 않습니다. 반복 가져오기 시 중복될 수 있으므로 기존 일정을 확인하세요.')
    st.divider()
    st.subheader('냉장고에 붙일 QR')
    url = st.text_input('실제 배포된 앱 HTTPS 주소', value=str(config.get('APP_URL', '')))
    p = urlparse(url.strip())
    if url and p.scheme == 'https' and p.netloc and not p.username and not p.password:
        out = io.BytesIO()
        qrcode.make(url.strip()).save(out, format='PNG')
        st.image(out.getvalue(), width=200)
        st.download_button('QR 다운로드', out.getvalue(), file_name='fridge-qr.png', mime='image/png')
    elif url:
        st.warning('올바른 HTTPS 앱 주소를 입력하세요.')
    st.caption('QR에는 앱 주소만 포함됩니다. 사진으로 신선도나 기한을 자동 추정하지 않습니다.')
    with st.expander('소진 기록'):
        for old in [x for x in items if not x.get('active', True)]:
            st.write(old['name'] + ' · ' + str(old.get('consumed', '')))
            if st.button('복원', key='restore_' + old['id']):
                write_record('item', dict(old, active=True, consumed=None), old['id'])
            confirm = st.checkbox('이 기록 영구 삭제', key='oldconfirm_' + old['id'])
            if st.button('삭제', key='olddelete_' + old['id'], disabled=not confirm):
                delete_record(old['id'])
    if password and st.button('로그아웃'):
        st.session_state.clear()
        st.rerun()
