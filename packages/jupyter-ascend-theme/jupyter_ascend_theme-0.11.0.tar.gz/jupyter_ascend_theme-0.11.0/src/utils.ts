import { appConfig, Links } from './configuration';
import { Icons } from './icons';

import appleTouchIcon from '../style/apple-touch-icon.png';
import faviconPng from '../style/favicon.png';
import logo from '../style/logo.png';

/**
 * Overrides the default document title and favicon.
 */
export const initiAppFaviconAndTitle = () => {
  const head = document.head;

  const iconLinks = head.querySelectorAll('link[rel="icon"]');
  const shortcutIconLinks = head.querySelectorAll('link[rel="shortcut icon"]');
  const appleTouchIconLinks = head.querySelectorAll(
    'link[rel="apple-touch-icon"]'
  );
  const busyIconLinks = head.querySelectorAll('link[type="image/x-icon"]');

  // Existent favicons set by JupyterLab
  [
    ...Array.from(iconLinks),
    ...Array.from(shortcutIconLinks),
    ...Array.from(appleTouchIconLinks),
    ...Array.from(busyIconLinks)
  ].forEach(favicon => {
    if (head.contains(favicon)) {
      head.removeChild(favicon);
    }
  });

  const linkIcon = document.createElement('link');
  linkIcon.rel = 'icon';
  linkIcon.type = 'image/png';
  linkIcon.href = faviconPng;
  linkIcon.setAttribute('sizes', '32x32');
  head.appendChild(linkIcon);

  const linkShortCut = document.createElement('link');
  linkShortCut.rel = 'shortcut icon';
  linkShortCut.type = 'image/png';
  linkShortCut.href = faviconPng;
  linkShortCut.setAttribute('sizes', '32x32');
  head.appendChild(linkShortCut);

  const linkAppleTouch = document.createElement('link');
  linkAppleTouch.rel = 'apple-touch-icon';
  linkAppleTouch.href = appleTouchIcon;
  linkAppleTouch.setAttribute('sizes', '180x180');
  head.appendChild(linkAppleTouch);

  const svgDataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(Icons.CGILogo)}`;
  const linkMaskIcon = document.createElement('link') as HTMLLinkElement & {
    color: string;
  };
  linkMaskIcon.rel = 'mask-icon';
  linkMaskIcon.type = 'image/svg+xml';
  linkMaskIcon.color = '#00ae9d';
  linkMaskIcon.href = svgDataUrl;
  head.appendChild(linkMaskIcon);

  Object.defineProperty(document, 'title', {
    set(_arg) {
      Object.getOwnPropertyDescriptor(
        Document.prototype,
        'title'
        // Edit the document.title property setter,
        // call the original setter function for document.title and make sure 'this' is set to the document object,
        // then overrides the value to set
      )?.set?.call(document, appConfig.appName);
    },
    configurable: true
  });
};

/**
 * Initializes the application header by adding various elements.
 */
export const initAppHeader = () => {
  initAppLogo();

  try {
    const userData = localStorage.getItem(
      '@jupyterlab/services:UserManager#user'
    );
    if (userData) {
      const user = JSON.parse(userData);

      if (user && user.name) {
        const headerContainerEl = document.createElement('div');
        headerContainerEl.classList.add('ascend-header-container');
        headerContainerEl.id = 'ascend-header-container';

        /** Create the icons */
        const iconsContainerEl = document.createElement('div');
        iconsContainerEl.classList.add('ascend-header-icons');

        if (appConfig.header.getInsulaAppsMenuLinks()) {
          const icon1 = document.createElement('span');
          icon1.innerHTML = Icons.AppsIcon;
          icon1.id = 'insulaAppsMenuLinks';
          icon1.addEventListener('click', () => {
            showHeaderMenu(
              appConfig.header.getInsulaAppsMenuLinks()!,
              icon1.id as 'insulaAppsMenuLinks',
              true
            );
          });
          iconsContainerEl.appendChild(icon1);
        }

        if (appConfig.header.otherInfoMenuLinks) {
          const icon2 = document.createElement('span');
          icon2.innerHTML = Icons.InfoIcon;
          icon2.id = 'otherInfoMenuLinks';
          icon2.addEventListener('click', () => {
            showHeaderMenu(
              appConfig.header.otherInfoMenuLinks!,
              icon2.id as 'otherInfoMenuLinks',
              false
            );
          });
          iconsContainerEl.appendChild(icon2);
        }

        headerContainerEl.appendChild(iconsContainerEl);

        /** Create the user name panel */
        const userNameContainerEl = document.createElement('div');
        userNameContainerEl.classList.add('ascend-header-user');

        const iconEl = document.createElement('span');
        iconEl.innerHTML = Icons.UserIcon;

        const spanEl = document.createElement('span');
        spanEl.innerText = user.name;

        userNameContainerEl.appendChild(iconEl);
        userNameContainerEl.appendChild(spanEl);

        headerContainerEl.appendChild(userNameContainerEl);

        document.body.appendChild(headerContainerEl);
      }
    }
  } catch (error) {
    console.error('Error parsing user data:', error);
  }
};

/**
 * Adds a custom logo to the application.
 */
export const initAppLogo = () => {
  const imgEl = document.createElement('img');
  imgEl.alt = 'Ascend Logo';
  imgEl.src = logo;

  const logoSectionEL = [
    document.getElementById('jp-MainLogo'),
    document.getElementById('jp-RetroLogo')
  ];

  // Append the logo image and text to each logo section
  logoSectionEL.forEach(el => {
    if (el) {
      el.appendChild(imgEl);
      const spanEl = document.createElement('span');
      spanEl.classList.add('jp-MainLogo-span');
      spanEl.innerHTML = appConfig.appName;
      el.appendChild(spanEl);
    }
  });
};

let currentOpenMenuId = '';

/**
 * Mounts or toggles the visibility of the header menu.
 *
 * @param links - The links to display in the menu.
 * @param id - An ID to identify the menu element.
 * @param avatar - If true, an avatar will be displayed next to each link.
 */
const showHeaderMenu = (
  links: Links,
  id: 'insulaAppsMenuLinks' | 'otherInfoMenuLinks',
  avatar: boolean
) => {
  const headerMenuContainerId = `ascend-header-menu-container-${id}`;
  let headerMenuContainerEl = document.getElementById(headerMenuContainerId);

  // Hide the currently open menu if it's different from the one being toggled
  if (!!currentOpenMenuId && currentOpenMenuId !== headerMenuContainerId) {
    const currentMenuEl = document.getElementById(currentOpenMenuId);
    if (currentMenuEl) {
      currentMenuEl.style.display = 'none';
    }
  }
  if (headerMenuContainerEl) {
    // Toggle visibility of the existing menu
    if (headerMenuContainerEl.style.display === 'block') {
      headerMenuContainerEl.style.display = 'none';
      currentOpenMenuId = '';
    } else {
      headerMenuContainerEl.style.display = 'block';
      currentOpenMenuId = headerMenuContainerId;
    }
  } else {
    // Create the menu container if it doesn't exist
    headerMenuContainerEl = document.createElement('div');
    headerMenuContainerEl.id = headerMenuContainerId;
    headerMenuContainerEl.classList.add('ascend-header-menu-container');

    const ulEl = document.createElement('ul');
    ulEl.classList.add('ascend-footer-menu-ul');

    links.forEach(link => {
      const liEl = document.createElement('li');
      const anchorEl = document.createElement('a');
      anchorEl.href = link.href;
      anchorEl.target = '_blank';
      anchorEl.innerText = link.label;
      liEl.appendChild(anchorEl);

      if (avatar) {
        const avatarLetter = link.label.charAt(0).toUpperCase();
        const spanEl = document.createElement('div');
        spanEl.innerText = avatarLetter;
        spanEl.classList.add('ascend-header-menu-avatar');
        anchorEl.before(spanEl);
      }

      ulEl.appendChild(liEl);
    });

    if (id === 'insulaAppsMenuLinks') {
      const paragraphEl = document.createElement('p');
      paragraphEl.innerText = 'Other Applications'.toUpperCase();
      headerMenuContainerEl.appendChild(paragraphEl);
    }

    headerMenuContainerEl.appendChild(ulEl);
    const menuButtonEl = document.getElementById(id);

    if (id === 'insulaAppsMenuLinks' && menuButtonEl) {
      headerMenuContainerEl.style.transform = 'translateX(-350px)';
    }

    menuButtonEl?.before(headerMenuContainerEl);

    currentOpenMenuId = headerMenuContainerId;
  }
};

document.addEventListener('mouseover', event => {
  if (currentOpenMenuId) {
    const menuDivEl = document.getElementById(currentOpenMenuId);

    if (menuDivEl && menuDivEl.style.display !== 'none') {
      if (
        !menuDivEl.contains(event.target as Node) &&
        !document
          .getElementById('ascend-header-container')
          ?.contains(event.target as Node)
      ) {
        menuDivEl.style.display = 'none';
        currentOpenMenuId = '';
      }
    }
  }
});
