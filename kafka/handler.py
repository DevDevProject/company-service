from db.session import get_db
from models.company import Company
import time
from models.company import BlogUpdateFailLog
from models.company import RecruitUpdateFailLog

def update_company_blog_count(company_name: str, retry: int = 3):
    db = next(get_db())
    try:
        company = db.query(Company).filter(Company.name == company_name).first()
        if company:
            company.blog_count += 1
            db.commit()
            print(f"성공 {company_name} 블로그 수 증가 → 현재 수: {company.blog_count}")
        else:
            print(f"실패 {company_name} 회사 없음")
    except Exception as e:
        print(f"🔥 {company_name} DB 업데이트 실패 (남은 재시도 {retry - 1}회): {e}")
        save_blog_fail_log(company_name, str(e))
    finally:
        db.close()
        
async def save_blog_fail_log(company_name: str, reason: str):
    db = next(get_db())
    try:
        company = db.query(Company).filter(Company.name == company_name).first()
        fail_log = BlogUpdateFailLog(
            company_id=company.id,
            error=reason
        )
        db.add(fail_log)
        db.commit()
    except Exception as e:
        print("f로그 저장 실패 {e}")
        db.rollback()
    finally:
        db.close()
        
def update_company_recruit_count(company_name: str, retry: int = 3):
    db = next(get_db())
    try:
        company = db.query(Company).filter(Company.name == company_name).first()
        if company:
            company.recruit_count += 1
            db.commit()
            print(f"성공 {company_name} 채용 공고 수 증가 → 현재 수: {company.recruit_count}")
        else:
            print(f"실패 {company_name} 회사 없음")
    except Exception as e:
        print(f"🔥 {company_name} DB 업데이트 실패 (남은 재시도 {retry - 1}회): {e}")
        save_recruit_fail_log(company_name, str(e))
    finally:
        db.close()
        
async def save_recruit_fail_log(company_name: str, reason: str):
    db = next(get_db())
    try:
        company = db.query(Company).filter(Company.name == company_name).first()
        fail_log = RecruitUpdateFailLog(
            company_id=company.id,
            error=reason
        )
        db.add(fail_log)
        db.commit()
    except Exception as e:
        print("f로그 저장 실패 {e}")
        db.rollback()
    finally:
        db.close()