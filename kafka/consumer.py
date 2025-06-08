import asyncio
import json
from aiokafka import AIOKafkaConsumer
from kafka.handler import update_company_blog_count
from kafka.handler import update_company_recruit_count
from dotenv import load_dotenv
import os

load_dotenv()

KAFKA_BLOG_TOPIC = "company.blog_count.increase"
KAFKA_RECRUIT_TOPIC = "company.recruit_count.increase"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

async def consume_blog_recruit_topics():
    consumer = AIOKafkaConsumer(
        KAFKA_BLOG_TOPIC,
        KAFKA_RECRUIT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="company-service",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    await consumer.start()
    try:
        print("🟢 Kafka blog-recruit 소비자 실행 중...")
        async for msg in consumer:
            topic = msg.topic
            data = msg.value
            company_name = data.get("company_name")

            if topic == KAFKA_BLOG_TOPIC:
                print(f"Blog Count 메시지 받음: {company_name}")
                await asyncio.to_thread(update_company_blog_count, company_name)

            elif topic == KAFKA_RECRUIT_TOPIC:
                print(f"Recruit Count 메시지 받음: {company_name}")
                await asyncio.to_thread(update_company_recruit_count, company_name)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume_blog_recruit_topics())
    
    
