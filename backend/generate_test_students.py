import asyncio
import os
import random
from database import get_async_supabase

async def generate_5000_students():
    supabase = await get_async_supabase()
    total_to_generate = 5000
    batch_size = 500
    
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry"]
    last_names = ["Doe", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez"]
    programs = ["BSIT", "BSCS", "BSECE", "BSME", "BSCE"]

    print(f"Starting generation of {total_to_generate} students...")

    for i in range(0, total_to_generate, batch_size):
        batch = []
        for j in range(batch_size):
            num = i + j + 1
            student_id = f"TEST-{num:04d}"
            name = f"{random.choice(first_names)} {random.choice(last_names)} {num}"
            program = random.choice(programs)
            year = random.randint(1, 4)
            
            batch.append({
                "student_id": student_id,
                "full_name": name,
                "program": program,
                "year_level": year,
                "has_voted": False
            })
        
        try:
            result = await supabase.table("students").insert(batch).execute()
            print(f"Successfully injected batch {i//batch_size + 1}/{total_to_generate//batch_size} ({len(batch)} students)")
        except Exception as e:
            print(f"Error injecting batch starting at {i}: {e}")
            # Continue to next batch or stop? For now continue.

    print("Generation complete!")

if __name__ == "__main__":
    asyncio.run(generate_5000_students())
