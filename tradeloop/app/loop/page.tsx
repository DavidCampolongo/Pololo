import { getSession, getUserDetails } from '@/app/supabase-server';
import { redirect } from 'next/navigation';
import API_Manager from '@/app/loop/API_Manager';

export default async function Loop4() {
  const [session, userDetails] = await Promise.all([
    getSession(),
    getUserDetails()  // will probably need later
    // pass prop for link button enabled/disabled status
  ]);

  const user_id = session?.user.id;  // will probably need later
  const account_name = userDetails?.bybit_account_name;
  const api_key = userDetails?.bybit_api_key;
  const api_secret = userDetails?.bybit_api_secret;
  const utid = userDetails?.uniqueTaskId;
  const link_status = userDetails?.link;

  if (!session) {
    return redirect('/signin');
  }

  return(
    // blank page with black background
    <API_Manager
      user_id={user_id}
      account_name={account_name}
      api_key={api_key}
      api_secret={api_secret}
      link_status={link_status}
      get_utid={utid}
    ></API_Manager>
  )
}