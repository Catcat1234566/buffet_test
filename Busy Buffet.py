import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplthai

# เรียกใช้ภาษาไทยทันที
mplthai.setup()

@st.cache_data
def load_data():
    # ตรวจสอบชื่อไฟล์ให้ตรงกับบน GitHub
    path = "2026 Data Test1 Final - Busy Buffet Dataset.xlsx"
    xl = pd.read_excel(path, sheet_name=None)
    
    day_names = ["133", "143", "153", "173", "183"]
    all_days = []
    
    # วนลูปอ่าน 5 แผ่นงานแรก
    for i, (sheet, df_sheet) in enumerate(xl.items()):
        if i < 5:
            df_sheet['day'] = day_names[i]
            all_days.append(df_sheet)
            
    data = pd.concat(all_days, ignore_index=True)
    
    # แปลงเวลาเป็นนาที
    def to_min(t):
        if pd.isna(t): return 0
        parts = str(t).split(':')
        try:
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0

    data['meal_min'] = data['meal_end'].apply(to_min) - data['meal_start'].apply(to_min)
    data['is_walkaway'] = data['meal_start'].isna() & data['queue_start'].notna()
    
    return data, day_names

df, day_list = load_data()
seated = df[df['meal_min'] > 0]

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(layout="wide")

st.title("Breakfast Buffet Analysis")
 
# --- Task 1: ความคิดเห็นของพนักงานแต่ละข้อเป็นความจริงหรือไม่ ---
st.header("Task 1: ความคิดเห็นของพนักงานแต่ละข้อเป็นความจริงหรือไม่")
t1_c1, t1_c2, t1_c3 = st.columns(3)
 
with t1_c1:
    st.markdown("**1.1 ลูกค้าในโรงแรม (In house) ไม่พอใจที่ต้องรอโต๊ะ ส่วนลูกค้าทั่วไป (Walk in) ก็ไม่พอใจเหมือนกัน เวลาที่พวกเขาต้องเข้าคิวนาน ๆ แล้วสุดท้ายก็ออกจากคิวไปเพราะไม่อยากรออีกต่อไปแล้ว**")
    wa_counts = df[df['is_walkaway']].groupby('day').size().reindex(day_list, fill_value=0)
    fig, ax = plt.subplots(figsize=(4, 3))
    bars = wa_counts.plot(kind="bar", color="orange", ax=ax)
    ax.set_ylabel("จำนวนกลุ่ม")
    for i, v in enumerate(wa_counts.values):
        ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold', fontsize=9)
    st.pyplot(fig)
    st.info(f"**เหตุผลที่ข้อนี้เป็นจริง:** ในข้อมูลจะมีกลุ่มลูกค้าที่พนักงานลงระบบไว้ในวัน 143 และ 153 มีลูกค้าที่เริ่มรอคิว (Queue Start) แต่ช่อง เริ่มกิน (Meal Start) กลับว่าง " 
            f"ซึ่งแสดงว่าลูกค้าเดินออกจากร้านไปทั้งที่ยังไม่ได้โต๊ะ แสดงว่าพวกเขารอไม่ไหว")
 
with t1_c2:
    st.markdown("**1.2 พวกเรายุ่งมากในทุก ๆ วันของสัปดาห์ ถ้ามันจะยุ่งขนาดนี้ทุกอาทิตย์ ฉันคิดว่ามันเป็นไปไม่ได้เลยที่จะประคองธุรกิจนี้ต่อไป ธุรกิจบุฟเฟต์แบบนี้มันไม่เหมาะกับโรงแรมของเราหรอก**")
    daily_guest_pax = seated.pivot_table(
        index='day', columns='Guest_type', values='pax', aggfunc='sum'
    ).reindex(day_list, fill_value=0)

    fig, ax = plt.subplots(figsize=(4, 3))
    daily_guest_pax.plot(kind="bar", stacked=True, color=["green", "blue"], ax=ax)
    ax.set_ylabel("จำนวนคน")
    ax.legend(title="ประเภทลูกค้า", loc='upper center',
              bbox_to_anchor=(0.5, 1.25), ncol=2, fontsize='small')
    totals = daily_guest_pax.sum(axis=1)
    for i, total in enumerate(totals):
        ax.text(i, total + 1, f'{total:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    st.pyplot(fig)
    st.info(f"**เหตุผลที่ข้อนี้เป็นจริง:** พนักงานยุ่งมากทุกวันจริง และจะเห็นว่าสัดส่วนลูกค้าทั่วไป (Walk in) " 
            f"มีปริมาณสูงมากกว่าหรือเท่ากับลูกค้าในโรงแรม (In house) ในทุกวัน ทำให้ภาระงานของพนักงานหนักกว่าปกติ")
 
with t1_c3:
    st.markdown("**1.3 ลูกค้าทั่วไป (Walk in) นั่งแช่ทั้งวัน มันเลยหาโต๊ะให้ลูกค้าในโรงแรม (In house) ได้ยากมาก เรามีโต๊ะไม่พอ ดังนั้นพอมีลูกค้าคนหนึ่งนั่งนานเกินไป มันเลยทำให้คิวยาวมาก**")
    daily_avg_time = seated.pivot_table(
        index='day', columns='Guest_type', values='meal_min', aggfunc='mean'
    ).reindex(day_list)

    fig, ax = plt.subplots(figsize=(4, 3))
    daily_avg_time.plot(kind="bar", ax=ax, color=["green", "blue"])
    ax.set_ylabel("นาทีเฉลี่ย")
    ax.set_xlabel("")
    ax.legend(title="ประเภทลูกค้า", loc='upper center',
              bbox_to_anchor=(0.5, 1.3), ncol=2, fontsize='small')
    n_groups = len(daily_avg_time)
    n_bars = len(daily_avg_time.columns)
    bar_width = 0.8 / n_bars
    for j, col in enumerate(daily_avg_time.columns):
        for i, v in enumerate(daily_avg_time[col]):
            if pd.notna(v):
                x_pos = i - 0.4 + bar_width * (j + 0.5)
                ax.text(x_pos, v + 0.5, f'{v:.0f}', ha='center', va='bottom',
                        fontsize=7, fontweight='bold')
    st.pyplot(fig)

    st.info(f"**เหตุผลที่ข้อนี้เป็นจริง:** กราฟแสดงให้เห็นว่าในทุกๆ วัน ลูกค้าทั่วไป (Walk in) " 
            f"ใช้เวลาทานเฉลี่ยสูงกว่าลูกค้าโรงแรม (In house) อย่างชัดเจน " 
            "โดยเฉพาะบางวันที่สูงมาก จึงแสดงให้เห็นว่าลูกคา Walk in นั่งแช่จริงในทุกวัน")
 
# --- Task 2: โต้แย้งแนวทางบริหาร ---
st.divider()
st.header("Task 2: สำหรับข้อเสนอแนะแต่ละข้อให้สร้าง Visuals และการวิเคราะห์เพื่อคัดค้านว่าทำไมวิธีเหล่านั้นถึงไม่ได้ผล")
t2_c1, t2_c2, t2_c3 = st.columns(3)
 
with t2_c1:
    st.markdown("**2.1 ลดระยะเวลาในการนั่งรับประทานอาหารจาก 5 ชั่วโมง ให้เหลือน้อยกว่านั้น**")
 
    inhouse_meals_21 = seated[seated['Guest_type'] == 'In house']['meal_min']
    walkin_meals_21  = seated[seated['Guest_type'] == 'Walk in']['meal_min']
    avg_in21   = inhouse_meals_21.mean()
    avg_walk21 = walkin_meals_21.mean()
 
    fig, axes = plt.subplots(1, 2, figsize=(6, 3))
 
    # กราฟซ้าย: bar เปรียบเทียบค่าเฉลี่ย vs เส้น 5 ชั่วโมง (300 นาที)
    ax = axes[0]
    ax.bar(['In house', 'Walkin'], [avg_in21, avg_walk21], color=['#1d9e75', '#3498db'])
    ax.axhline(300, color='red', linestyle='--', linewidth=1.2, label='5 ชม. (300 น.)')
    ax.set_ylabel("นาทีเฉลี่ย")
    ax.set_title("เฉลี่ยเทียบ 5 ชั่วโมง", fontsize=9)
    ax.set_ylim(0, 340)
    ax.legend(fontsize=7)
    for i, v in enumerate([avg_in21, avg_walk21]):
        ax.text(i, v + 5, f'{v:.0f} น.', ha='center', fontweight='bold', fontsize=9)
 
    # กราฟขวา: distribution Walk-in พร้อมเส้น threshold ต่าง ๆ
    ax2 = axes[1]
    ax2.hist(walkin_meals_21, bins=20, color='#3498db', alpha=0.8)
    ax2.axvline(300, color='red',    linestyle='--', linewidth=1.2, label='5 ชม.')
    ax2.axvline(avg_walk21, color='orange', linestyle='-', linewidth=1.2, label=f'เฉลี่ย {avg_walk21:.0f} น.')
    ax2.set_xlabel("นาที")
    ax2.set_ylabel("จำนวนกลุ่ม")
    ax2.set_title("การกระจาย Walk-in", fontsize=9)
    ax2.legend(fontsize=7)
 
    plt.tight_layout()
    st.pyplot(fig)
 
    pct_walkin_under300 = (walkin_meals_21 < 300).mean() * 100
    st.warning(
        f"**โต้แย้ง:** นโยบายนี้ **ไม่ช่วยอะไรเลย** เพราะ Walk-in ถึง {pct_walkin_under300:.0f}% "
        f"ทานเสร็จก่อนถึง 5 ชั่วโมงอยู่แล้ว (เฉลี่ยแค่ {avg_walk21:.0f} นาที) "
        f"การลดจาก 300 นาที → เช่น 240 หรือ 180 นาที จึงไม่กระทบพฤติกรรมลูกค้าจริง ๆ เลย "
        f"โต๊ะก็หมุนเวียนได้ไม่เร็วขึ้น ปัญหาคิวยังอยู่เหมือนเดิม "
        f"ถ้าจะให้ 'ได้ผลจริง' ต้องลดลงมาถึงประมาณ 90 นาที "
        f"ซึ่งนั่นเป็นคนละนโยบายและต้องออกแบบใหม่ทั้งหมด "
    )
 
with t2_c2:
    st.markdown("**2.2 ปรับราคาขึ้นเป็น 259 บาท ในทุก ๆ วัน**")
 
    price_new = 259
    avg_in22   = seated[seated['Guest_type'] == 'In house']['meal_min'].mean()
    avg_walk22 = seated[seated['Guest_type'] == 'Walk in']['meal_min'].mean()
    cost_inhouse22 = price_new / avg_in22
    cost_walkin22  = price_new / avg_walk22
 
    fig, axes = plt.subplots(1, 2, figsize=(6, 3))
 
    ax = axes[0]
    bars = ax.bar(['In house', 'Walk in'], [cost_inhouse22, cost_walkin22],
                  color=['#1d9e75', '#e74c3c'])
    ax.set_ylabel("บาท / นาที")
    ax.set_title("ราคา 259 บ. ÷ เวลานั่ง", fontsize=9)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.05,
                f'{h:.2f} บ./น.', ha='center', va='bottom', fontweight='bold', fontsize=9)
 
    # กราฟขวา: จำนวนคนสัดส่วน In-house vs Walk-in รายวัน → ถ้า in-house ลด Walk-in ยิ่งครอง
    ax2 = axes[1]
    pax_by_day = seated.pivot_table(index='day', columns='Guest_type', values='pax',
                                    aggfunc='sum').reindex(day_list, fill_value=0)
    pax_by_day.plot(kind='bar', stacked=True, color=['#1d9e75', '#3498db'],
                    ax=ax2, legend=True)
    ax2.set_xticklabels([d.replace('วัน ', '') for d in day_list], rotation=0, fontsize=8)
    ax2.set_ylabel("จำนวนคน")
    ax2.set_title("สัดส่วนจำนวนคนรายวัน", fontsize=9)
    ax2.legend(fontsize=7, loc='upper right')
 
    plt.tight_layout()
    st.pyplot(fig)
 
    st.warning(
        f"**โต้แย้ง:** ขึ้นราคาทำให้ In-house รู้สึก **'ไม่คุ้ม'** ทันที "
        f"เพราะจ่ายราคาเดียวกัน {price_new} บาท แต่ได้นั่งเพียง {avg_in22:.0f} นาทีเฉลี่ย "
        f"(={cost_inhouse22:.2f} บ./น.) ขณะที่ Walk-in ได้ {avg_walk22:.0f} นาที "
        f"(={cost_walkin22:.2f} บ./น.) In-house จ่ายแพงกว่าต่อนาทีถึง "
        f"{cost_inhouse22/cost_walkin22:.1f} เท่า "
        f"ผลคือแขกโรงแรมจะหลีกเลี่ยงบุฟเฟต์นี้ ยิ่งทำให้ Walk-in ครองโต๊ะมากขึ้น "
        f"ปัญหาเดิมก็จะไม่ลดลงเลย"
    )
 
with t2_c3:
    st.markdown("**2.3 ให้สิทธิ์ลูกค้าที่พักในโรงแรมแซงคิวได้**")
 
    # โต๊ะรวมตาม Appendix: Indoor 1A-6B = 12, Outdoor split 7A-11B = 13, Full 12-15 = 4 → รวม 29
    total_units = 29
 
    # กราฟ 1: จำนวนโต๊ะที่ถูกล็อคโดยกลุ่มนั่งนาน >90 นาที แยกรายวัน
    long_stay_data = seated[seated['meal_min'] >60]
    busy_per_day = long_stay_data.groupby('day')['table_no.'].nunique().reindex(day_list, fill_value=0)
    free_per_day = (total_units - busy_per_day).clip(lower=0)
 
    fig, axes = plt.subplots(1, 2, figsize=(6, 3))
 
    # กราฟซ้าย: โต๊ะที่มีคนนั่ง vs ว่าง รายวัน
    ax = axes[0]
    x = range(len(day_list))
    ax.bar(x, busy_per_day.values, color='#e74c3c', label='โต๊ะที่มีคนนั่ง > 60 นาที')
    ax.bar(x, free_per_day.values, bottom=busy_per_day.values, color='#1d9e75', label='ว่าง')
    ax.axhline(total_units, color='gray', linestyle='--', linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels([d.replace('วัน ', '') for d in day_list], fontsize=8)
    ax.set_ylabel("จำนวนโต๊ะ")
    ax.set_ylim(0, 33)
    ax.legend(fontsize=7)
    ax.set_title("โต๊ะที่มีคนนั่ง vs ว่าง รายวัน", fontsize=9)
    ax.text(len(day_list)-0.5, total_units+0.5, f'ทั้งหมด {total_units}', fontsize=7, color='gray')
 
    # เวลารอเฉลี่ยของคนที่ต้องรอคิว
    df['wait_min'] = df['queue_end'].apply(
        lambda t: 0 if pd.isna(t) else int(str(t).split(':')[0])*60 + int(str(t).split(':')[1])
    ) - df['queue_start'].apply(
        lambda t: 0 if pd.isna(t) else int(str(t).split(':')[0])*60 + int(str(t).split(':')[1])
    )
    waited_df = df[df['wait_min'] > 0]
    avg_wait_by_day = waited_df.groupby('day')['wait_min'].mean().reindex(day_list, fill_value=0)
 
    ax2 = axes[1]
    ax2.bar(range(len(day_list)), avg_wait_by_day.values, color='#e67e22')
    ax2.set_xticks(list(range(len(day_list))))
    ax2.set_xticklabels([d.replace('วัน ', '') for d in day_list], fontsize=8)
    ax2.set_ylabel("นาทีเฉลี่ย")
    ax2.set_title("เวลารอคิวเฉลี่ย (นาที)", fontsize=9)
    for i, v in enumerate(avg_wait_by_day.values):
        if v > 0:
            ax2.text(i, v + 0.5, f'{v:.0f}', ha='center', fontsize=8, fontweight='bold')
 
    plt.tight_layout()
    st.pyplot(fig)
 
    avg_busy = busy_per_day.mean()
    avg_free = free_per_day.mean()
    avg_wait = waited_df['wait_min'].mean()
    st.warning(
        f"**โต้แย้ง:** ปัญหาคือ **ขาดโต๊ะว่าง** "
        f"เฉลี่ยแต่ละวันมีโต๊ะที่มีคนนั่ง **{avg_busy:.1f} จาก {total_units} units ({avg_busy/total_units*100:.0f}%)** "
        f"เหลือโต๊ะว่างเพียง {avg_free:.1f} units และผู้ที่ต้องรอคิวรอนานเฉลี่ย **{avg_wait:.0f} นาที** "
        f"การให้สิทธิ์แซงคิวจึงเท่ากับพาแขกโรงแรมมายืนรอ 'หน้าคิว' แทน 'ท้ายคิว' "
        f"แต่สุดท้ายก็ยังต้องรออยู่ดี ตราบใดที่โต๊ะ {avg_busy:.1f} units ยังไม่ลุก"
    )
 
# --- Task 3: แนวทางแก้ไขที่แนะนำ ---
st.divider()
st.header("Task 3: แนวทางแก้ไขที่แนะนำ กำหนด Time Limit 90 นาทีสำหรับ Walk in")
 
st.info(
    "**แนวทางที่เลือก:** ปรับเวลานั่งจาก 5 ชั่วโมง กำหนดเป็น **เวลาสูงสุด 90 นาทีสำหรับลูกค้า Walk in** โดยเฉพาะ "
    "(In house ไม่จำกัด เพื่อรักษาประสบการณ์แขกโรงแรม) "
)
 
t3_c1, t3_c2, t3_c3 = st.columns(3)
 
with t3_c1:
    st.markdown("**กราฟ 1: การกระจายเวลานั่งของ Walk in**")
 
    walkin_meals = seated[seated['Guest_type'] == 'Walk in']['meal_min']
    inhouse_meals = seated[seated['Guest_type'] == 'In house']['meal_min']
 
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.hist(walkin_meals, bins=20, color='#3498db', alpha=0.7, label='Walk in')
    ax.hist(inhouse_meals, bins=20, color='#1d9e75', alpha=0.7, label='In house')
    ax.axvline(90, color='red', linestyle='--', linewidth=1.5, label='เส้น 90 นาที')
    ax.set_xlabel("ระยะเวลานั่ง (นาที)")
    ax.set_ylabel("จำนวนกลุ่ม")
    ax.legend(fontsize=8)
    ax.set_title("การกระจายเวลานั่ง", fontsize=10)
 
    pct_walkin_over90 = (walkin_meals >= 90).mean() * 100
    pct_inhouse_over90 = (inhouse_meals >= 90).mean() * 100
    ax.text(95, ax.get_ylim()[1]*0.85,
            f'Walk in >{90}น.: {pct_walkin_over90:.1f}%\nIn house >{90}น.: {pct_inhouse_over90:.1f}%',
            fontsize=8, color='red',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff3f3', edgecolor='red', alpha=0.8))
    st.pyplot(fig)
    st.success(
        f"In house **{100-pct_inhouse_over90:.0f}%** ทานเสร็จก่อน 90 นาที เส้น 90 นาทีไม่กระทบลูกค้า In house เลย "
        f"แต่จะกระทบลูกค้า Walk in ที่นั่งนานเกิน ({pct_walkin_over90:.0f}% ของ walk in)"
    )
 
with t3_c2:
    st.markdown("**กราฟ 2: Simulation — โต๊ะที่ได้คืนถ้า cap Walk in ที่ 90 นาที**")
 
    # จำลองว่าถ้า walk-in ถูก cap ที่ 90 นาที โต๊ะที่เคยถูกล็อคจะลดลงเท่าไหร่
    walkin_over90_per_day = (
        seated[(seated['Guest_type'] == 'Walk in') & (seated['meal_min'] > 90)]
        .groupby('day').size().reindex(day_list, fill_value=0)
    )
 
    long_stay_all = seated[seated['meal_min'] > 60]
    busy_before = long_stay_all.groupby('day')['table_no.'].nunique().reindex(day_list, fill_value=0)
 
    # หลัง cap: กลุ่ม walk-in ที่เคยนาน >90 จะเหลือแค่ 90 นาที ไม่ถูกนับว่า 'โต๊ะที่มีคนนั่ง' นาน
    walkin_still_long = (
        seated[(seated['Guest_type'] == 'Walk in') & (seated['meal_min'] > 60) & (seated['meal_min'] <= 90)]
        .groupby('day')['table_no.'].nunique().reindex(day_list, fill_value=0)
    )
    inhouse_long = (
        seated[(seated['Guest_type'] == 'In house') & (seated['meal_min'] > 60)]
        .groupby('day')['table_no.'].nunique().reindex(day_list, fill_value=0)
    )
    busy_after = (walkin_still_long + inhouse_long).reindex(day_list, fill_value=0)
    tables_freed = (busy_before - busy_after).clip(lower=0)
 
    fig, ax = plt.subplots(figsize=(5, 4))
    x = range(len(day_list))
    w = 0.35
    bars1 = ax.bar([i - w/2 for i in x], busy_before.values, width=w, color='#e74c3c', label='ก่อน cap')
    bars2 = ax.bar([i + w/2 for i in x], busy_after.values, width=w, color='#1d9e75', label='หลัง cap 90 นาที')
    ax.set_xticks(list(x))
    ax.set_xticklabels([d.replace('วัน ', '') for d in day_list], fontsize=8)
    ax.set_ylabel("โต๊ะที่ถูกล็อค (units)")
    ax.set_title("โต๊ะถูกล็อค: ก่อน vs หลัง cap", fontsize=10)
    ax.legend(fontsize=8)
    for i, v in enumerate(tables_freed.values):
        if v > 0:
            ax.text(i + w/2, busy_after.values[i] + 0.3, f'-{v}', ha='center', fontsize=8, color='green', fontweight='bold')
    st.pyplot(fig)
    st.success(
        f"หลังจากโต๊ะที่ถูกล็อคลดลงเฉลี่ย **{tables_freed.mean():.1f} units/วัน** "
        f"คิดเป็น {tables_freed.mean()/busy_before.mean()*100:.0f}% ของโต๊ะที่มีคนนั่ง "
        f"โต๊ะเหล่านี้หมุนเวียนได้เร็วขึ้น"
    )
 
with t3_c3:
    st.markdown("**กราฟ 3: เวลา Walk in ที่เกิน 90 นาที เวลาที่สูญเสียไป**")
 
    walkin_over90_grp = seated[(seated['Guest_type'] == 'Walk in') & (seated['meal_min'] > 90)].copy()
    walkin_over90_grp['extra_min'] = walkin_over90_grp['meal_min'] - 90
 
    extra_by_day = walkin_over90_grp.groupby('day')['extra_min'].sum().reindex(day_list, fill_value=0)
    count_by_day = walkin_over90_grp.groupby('day').size().reindex(day_list, fill_value=0)
 
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(range(len(day_list)), extra_by_day.values, color='#e67e22')
    ax.set_xticks(list(range(len(day_list))))
    ax.set_xticklabels([d.replace('วัน ', '') for d in day_list], fontsize=8)
    ax.set_ylabel("นาทีรวมที่เกิน 90 นาที")
    ax.set_title("'เวลาโต๊ะ' ที่สูญเสียรายวัน\n(Walk-in ที่นั่งเกิน 90 นาที)", fontsize=9)
    for i, (bar, cnt) in enumerate(zip(bars, count_by_day.values)):
        h = bar.get_height()
        if h > 0:
            ax.text(i, h + 5, f'{h:.0f} น.\n({cnt} กลุ่ม)', ha='center', fontsize=7.5, fontweight='bold')
    st.pyplot(fig)
 
    total_extra = extra_by_day.sum()
    total_grps = count_by_day.sum()
    st.success(
        f"ใน 5 วัน Walk in ที่นั่งเกิน 90 นาที มีทั้งหมด **{total_grps} กลุ่ม** "
        f"รวมเวลาเกินกว่า **{total_extra} นาที ({total_extra//60} ชม. {total_extra%60} น.)** "
        f"ถ้าเวลานี้ถูกคืนให้โต๊ะ จะรองรับกลุ่มใหม่เพิ่มได้อีกมาก"
    )
 
st.divider()
st.subheader("สรุปเหตุผลที่เลือกแนวทางนี้")
st.success("""
**ทำไม Time Limit 90 นาที (เฉพาะ Walk-in) ถึงเป็นทางออกที่ดีที่สุด**
 
1.In house 94% ทานเสร็จก่อน 90 นาที นโยบายนี้ไม่กระทบแขกโรงแรมแทบเลย ขณะที่ Walk in 27.6% นั่งเกิน 90 นาที และเป็นกลุ่มที่ทำให้โต๊ะหมุนเวียนช้า

2.แยกเป็น Walk in เท่านั้น ไม่กระทบ In-houseพนักงานสามารถแจ้งลูกค้าตอน check in คิว ว่ามี time limit 90 นาทีสำหรับ Walk in เพื่อให้ลูกค้ารับรู้ตั้งแต่ต้น และสามารถจัดการคิวได้ง่ายขึ้น

""")
