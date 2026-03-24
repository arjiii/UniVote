import asyncio
from database import get_async_supabase

async def cleanup_test_students():
    supabase = await get_async_supabase()
    
    print("WARNING: This will delete ALL students with ID starting with 'TEST-'.")
    
    while True:
        print("Searching for next batch of test students (1,000 limit)...")
        test_students = await supabase.table("students").select("id").like("student_id", "TEST-%").limit(1000).execute()
        uuids = [s["id"] for s in (test_students.data or [])]
        
        if not uuids:
            print("No more test students found.")
            break

        print(f"Processing {len(uuids)} test students. Deleting their votes first...")
        
        # Batch delete votes (UUIDs in the list)
        batch_size = 100
        for i in range(0, len(uuids), batch_size):
            batch = uuids[i:i + batch_size]
            await supabase.table("votes").delete().in_("student_id", batch).execute()
        
        print(f"Deleting student records for this batch...")
        for i in range(0, len(uuids), batch_size):
            batch = uuids[i:i + batch_size]
            await supabase.table("students").delete().in_("id", batch).execute()
        print(f"Batch complete. Continuing search...")
    
    print("Cleanup process finished!")

if __name__ == "__main__":
    asyncio.run(cleanup_test_students())
