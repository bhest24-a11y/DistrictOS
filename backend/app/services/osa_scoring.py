from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from ..models import DailyPOS, OSAAlert, Store

def calculate_osa_alerts(db: Session, target_date: date = None):
    """
    Run nightly. Flags likely out-of-shelf SKUs based on 28-day velocity.
    """
    if not target_date:
        target_date = date.today() - timedelta(days=1)  # yesterday
    
    lookback_start = target_date - timedelta(days=28)
    
    # Step 1: Get 28-day baseline for active SKUs
    baseline_subq = db.query(
        DailyPOS.store_id,
        DailyPOS.sku,
        func.avg(DailyPOS.units_sold).label('avg_daily_units'),
        func.count(DailyPOS.id).label('selling_days'),
        func.max(DailyPOS.business_date).label('last_sale_date')
    ).filter(
        DailyPOS.business_date >= lookback_start,
        DailyPOS.business_date < target_date,
        DailyPOS.units_sold > 0
    ).group_by(DailyPOS.store_id, DailyPOS.sku).subquery()
    
    # Step 2: Join yesterday's actuals to baseline
    results = db.query(
        DailyPOS,
        baseline_subq.c.avg_daily_units,
        baseline_subq.c.selling_days,
        baseline_subq.c.last_sale_date,
        Store.store_name,
        Store.district
    ).join(
        baseline_subq,
        and_(
            DailyPOS.store_id == baseline_subq.c.store_id,
            DailyPOS.sku == baseline_subq.c.sku
        )
    ).outerjoin(
        Store, DailyPOS.store_id == Store.store_id
    ).filter(
        DailyPOS.business_date == target_date,
        baseline_subq.c.selling_days >= 8,  # active SKU
        baseline_subq.c.avg_daily_units >= 2.0  # expected 2+ units
    ).all()
    
    alerts_to_insert = []
    for row in results:
        pos, avg_daily_units, selling_days, last_sale_date, store_name, district = row
        
        # CORE OSA LOGIC: Sold 0 yesterday but should have sold 2+
        if pos.units_sold == 0:
            days_since_sale = (target_date - last_sale_date).days
            
            if days_since_sale <= 7:  # sold within last week
                confidence = min(0.95, 0.4 + (selling_days/28.0)*0.3 + min(0.25, avg_daily_units/10.0))
                est_missed = float(avg_daily_units * pos.avg_unit_price) if pos.avg_unit_price else 0
                
                alerts_to_insert.append(OSAAlert(
                    business_date=target_date,
                    store_id=pos.store_id,
                    sku=pos.sku,
                    sku_description=pos.sku_description,
                    category=pos.category,
                    expected_units=round(avg_daily_units, 2),
                    actual_units=0,
                    days_since_last_sale=days_since_sale,
                    confidence=round(confidence, 2),
                    est_missed_sales=round(est_missed, 2),
                    likely_oos_flag=True
                ))
    
    # Clear old alerts for this date, insert new
    db.query(OSAAlert).filter(OSAAlert.business_date == target_date).delete()
    db.add_all(alerts_to_insert)
    db.commit()
    
    return len(alerts_to_insert)