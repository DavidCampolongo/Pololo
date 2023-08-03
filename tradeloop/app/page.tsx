import Button from '@/components/ui/Button';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-black text-center">
      <div className="flex flex-col items-center justify-center space-y-5">
        <img src="/TradeLoop.png" alt="Welcome to TradeLoop!" className="w-auto max-h-32" />
        <Link href={"/signin"} passHref>
          <Button
            variant="slim"
            type="button"
            className="px-6 py-3 mt-4 font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-md"
          >
            Coming Soon
          </Button>
        </Link>
      </div>
    </main>
  );
}