'use client'

import React, { ReactNode, useState, useEffect } from 'react';
import Button from '@/components/ui/Button';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

interface Props {
  user_id?: string;
  account_name?: string | null;
  api_key?: string | null;
  api_secret?: string | null;
  link_status?: boolean;
  get_utid?: string | null;
}

const API_Manager: React.FC<Props> = ({ user_id, account_name, api_key, api_secret, link_status, get_utid }) => {
  const [isLoading, setIsLoading] = useState(false);

  //temp ts fix
  const id = user_id || ''
  const name = account_name || null
  const key = api_key || null
  const secret = api_secret || null
  const link = link_status || false
  const utid = get_utid || null
  // think of adding utid to sync query to better optimize

  useEffect(() => {
    if (!link && !!utid) {  // if link is false & utid exists
      handleRefresh().catch((error) => {
        console.error("Error during initial fetch:", error);
      });
    }
  }, [])  // handles edge case of user refreshing page

  const handleRefresh = async() => {
    // if (!link && !!utid) {  // if link is false & utid exists
    toast.info('resuming sync', {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
      theme: "dark",
    });
    let status3 = 'Processing';
    let json3 // temp fix
    // did not account for utid does not exist
    while (status3 == 'Processing') {
      const res3 = await fetch(`https://tradeloop.app/api/sync?id=${encodeURIComponent(id)}`)
      json3 = await res3.json();
      status3 = json3.message
      console.log(json3)
      // maybe only do toast if not 'Processed'
      toast.info(`Status: ${json3.message}`, {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "dark",
      });
      await delay(5000)  // Implement max_timeout
    }
    if (json3.message == 'Processed') {
      console.log(`${json3}: Head over to the dashboard!`)
      toast.success('Received export from Bybit', {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "dark",
      });
    } else {  // if (json3.message == 'Failed')  //TODO maybe not?
      console.log(`${json3}: Please delete and try again`)
      toast.error(`${json3.message}: Please delete and try again`, {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "dark",
      });
    }
  }  // handles edge case of user refreshing page

  const handleClick = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();  // Prevent the default form submission behavior
    const formData = new FormData(event.currentTarget);

    setIsLoading(true);
    // await delay(5000)  // remove for prod
    // Probably use some sort of state management to represent each fetch
    // For production, convert console logs into json.message and toast/noti

    const name = formData.get('account_name') as string;
    const key = formData.get('api_key') as string;
    const secret = formData.get('api_secret') as string;
    const res = await fetch(`https://tradeloop.app/api/link.py?id=${encodeURIComponent(id)}&account_name=${encodeURIComponent(name)}&key=${encodeURIComponent(key)}&secret=${encodeURIComponent(secret)}`);
    let json = await res.json();
    // console.log(json)
    if (json.message == 'success') {
      toast.success('API check passed', {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "dark",
      });
      toast.info('Requested export from Bybit', {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "dark",
      });
      let status = 'Processing';
      let json2 // temp fix
      // did not account for utid does not exist
      while (status == 'Processing') {
        await delay(5000)  // Implement max_timeout
        const res2 = await fetch(`https://tradeloop.app/api/sync.py?id=${encodeURIComponent(id)}&account_name=${encodeURIComponent(name)}&key=${encodeURIComponent(key)}&secret=${encodeURIComponent(secret)}`)
        json2 = await res2.json();
        status = json2.message
        console.log(json2)
        // maybe only do toast if not 'Processed'
        toast.info(`Status: ${json2.message}`, {
          position: "top-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          theme: "dark",
        });
      }
      if (json2.message == 'Processed') {
        console.log(`${json2}: Head over to the dashboard!`)
        toast.success('Received export from Bybit', {
          position: "top-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          theme: "dark",
        });
      } else {  // if (json2.message == 'Failed')  //TODO maybe not?
        console.log(`${json2}: Please delete and try again`)
        toast.error(`${json2.message}: Please delete and try again`, {
          position: "top-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          theme: "dark",
        });
      }
    }
    else {
      console.log(json)
      // message = api check failed or export error
      toast.error(`${json.message}`, {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "dark",
      });
    }

    // console.log(json);
    setIsLoading(false);
  };


  return (
    <section className="mb-32 bg-black">
      <div className="max-w-6xl px-4 py-8 mx-auto sm:px-6 sm:pt-24 lg:px-8">
        <div className="sm:align-center sm:flex sm:flex-col">
          <h1 className="text-4xl font-extrabold text-white sm:text-center sm:text-6xl">
            Manage API
          </h1>
          <p className="max-w-2xl m-auto mt-5 text-xl text-zinc-200 sm:text-center sm:text-2xl">
            Powered by TradeLoop
          </p>
        </div>
      </div>
      <div className="p-4">
        <Card
          title="Connect to Bybit"
          description="Please enter API details."
          footer={
            <div className="flex flex-col items-start justify-between sm:flex-row sm:items-center">
              <p className="pb-4 sm:pb-0">
                READ-ONLY API
              </p>
              <Button
                variant="slim"
                type="submit"
                form="apiForm"
                disabled={!!utid || link}
                loading={isLoading}
              >
                {/* WARNING - In Next.js 13.4.x server actions are in alpha and should not be used in production code! */}
                Link
              </Button>
            </div>
          }
        >
          <div className="mt-8 mb-4 text-xl font-semibold">
            <form id="apiForm" onSubmit={handleClick}>
              <div className="flex flex-col sm:flex-row">
                <input
                  type="text"
                  name="account_name"
                  className="w-full sm:w-1/2 p-3 rounded-md bg-zinc-800 mb-2 sm:mb-0 sm:ml-2"
                  defaultValue={name ?? undefined}
                  placeholder="Account Name"
                  maxLength={15}
                  disabled={!!utid || link || isLoading}
                />
                <input
                  type="text"
                  name="api_key"
                  className="w-full sm:w-1/2 p-3 rounded-md bg-zinc-800 mb-2 sm:mb-0 sm:ml-2"

                  defaultValue={key ?? undefined}
                  placeholder="API Key"
                  maxLength={18}
                  disabled={!!utid || link || isLoading}
                />
                <input
                  type="text"
                  name="api_secret"
                  className="w-full sm:w-1/2 p-3 rounded-md bg-zinc-800 mb-2 sm:mb-0 sm:ml-2"
                  defaultValue={secret ? '************************************' : undefined}
                  placeholder="API Secret"
                  maxLength={36}
                  disabled={!!utid || link || isLoading}
                />
              </div>
            </form>
          </div>
        </Card>
      </div>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </section>
  )
}

interface Props_2 {
  title: string;
  description?: string;
  footer?: ReactNode;
  children: ReactNode;
}

function Card({ title, description, footer, children }: Props_2) {
  return (
    <div className="w-full max-w-3xl m-auto my-8 border rounded-md p border-zinc-700">
      <div className="px-5 py-4">
        <h3 className="mb-1 text-2xl font-medium">{title}</h3>
        <p className="text-zinc-300">{description}</p>
        {children}
      </div>
      <div className="p-4 border-t rounded-b-md border-zinc-700 bg-zinc-900 text-zinc-500">
        {footer}
      </div>
    </div>
  );
}

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default API_Manager;
