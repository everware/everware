# This adds the ability to modify the GithHub username whitelist
# without having to restart the hub. Use this together
# with GitHubOAuthenticator
# Create whitelist.txt in the top level directory, listing one allowed
# username per line

import everware

authenticator = everware.GitHubOAuthenticator
whitelist_file = 'whitelist.txt'
whitelist_handler = everware.DefaultWhitelistHandler(whitelist_file,
                                                     c,
                                                     authenticator)
