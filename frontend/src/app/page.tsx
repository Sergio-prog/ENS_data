"use client"

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Home() {
  const router = useRouter();
  const [domainToSearch, setDomainToSearch] = useState<string | null>();
  const domainExamples = ["uniswap.eth", "ens.eth", "vitalik.eth", "aave.eth", "uni.eth", "base.eth", "nick.eth"];

  const getRandomDomain = () => {
    return domainExamples[Math.floor(Math.random() * domainExamples.length)];
  }

  const redirectUrlTo = () => {
    if (!domainToSearch) {
      return;
    }
    
    router.push(process.env.NEXT_PUBLIC_API_URL + `/${domainToSearch}`);
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-8">
      {/* <div className="w-full mx-auto flex flex-col items-center justify-center"> */}
      <div className="flex flex-col w-full max-w-xl px-1">
          <label className="font-bold text-2xl ens-style-gradient bg-clip-text">
            Resolve domain
          </label>
      </div>

      <input 
        type="text" 
        value={domainToSearch || undefined}
        onChange={(e) => setDomainToSearch(e.target.value)}
        spellCheck={false} 
        autoComplete="off"
        autoCorrect="off"
        name="domain_input"
        placeholder={getRandomDomain()} 
        className="p-4 border border-stone-300 drop-shadow-sm hover:drop-shadow-md focus:drop-shadow-md short-transition max-w-xl
         w-full rounded-lg text-xl text-gray-800 appearance-none outline-none"
      />

      <button 
        className="py-4 px-7 mt-7 text-xl bg-blue-400 ens-style-gradient rounded-lg drop-shadow-md hover:drop-shadow-xl short-transition"
        type="button"
        onClick={redirectUrlTo}
      ><span className="text-white">Search</span></button>
        {/* </div> */}
    </main>
  );
}
