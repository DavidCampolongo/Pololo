import { getSession, getUserDetails } from '@/app/supabase-server';
import { redirect } from 'next/navigation';

export default async function Loop4() {
  const [session, userDetails] = await Promise.all([
    getSession(),
    getUserDetails()  // will probably need later
  ]);

  const user_id = session?.user.id;  // will probably need later

  // comment this conditional statement if you want to test without signing in
  if (!session) {
    return redirect('/signin');
  }

  return(
    // blank page with black background
    <section className="mb-32 bg-black"></section>
  )
}