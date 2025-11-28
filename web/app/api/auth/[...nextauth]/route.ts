// web/app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import type { NextAuthOptions } from "next-auth";

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Validate required environment variables
const googleClientId = process.env.GOOGLE_CLIENT_ID;
const googleClientSecret = process.env.GOOGLE_CLIENT_SECRET;

if (!googleClientId || !googleClientSecret) {
  console.warn(
    "Warning: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is not set. Google authentication will not work."
  );
}

const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: googleClientId || "",
      clientSecret: googleClientSecret || "",
    }),
  ],
  callbacks: {
    async signIn({ user, account }) {
      // Sync user to our backend on sign in
      if (account?.provider === "google" && user.email) {
        try {
          await fetch(`${apiUrl}/api/user/web`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: user.email,
              name: user.name || user.email,
              google_id: account.providerAccountId || "",
            }),
          });
        } catch (error) {
          console.error("Error syncing user to backend:", error);
        }
      }
      return true;
    },
    async session({ session, token }) {
      // Add user email to session for API calls
      if (session.user && token.email) {
        session.user.email = token.email as string;
      }
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        token.email = user.email;
      }
      return token;
    },
  },
  pages: {
    signIn: "/profile",
    error: "/profile",
  },
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
