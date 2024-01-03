var locale = document.getElementsByTagName('html')[0].getAttribute('lang');

var privacyPolicyURL = '/en/protection-of-personal-data';

switch (locale) {
  case 'nl-BE':
    privacyPolicyURL = '/nl/bescherming-van-persoonsgegevens';
    break;
  case 'de-BE':
    privacyPolicyURL = '/de/datenschutz';
    break;
  case 'fr-BE':
    privacyPolicyURL = '/fr/protection-des-donnees-personnelles';
    break;
};

window.orejimeConfig = {
    appElement: "body",
    privacyPolicy: privacyPolicyURL,
    default: false,
    mustConsent: false,
    mustNotice: false,
    gdprCompliant: true,
    implicitConsent: false,
    lang: locale,
    translations: {
      'fr-BE': {
        "consentModal": {
            "title": "Nous utilisons des cookies",
            "description": "Quels cookies utilisons-nous et pourquoi ?",
            "privacyPolicy": {
                "name": "Politique d'utilisation des cookies",
                "text": "D\u00e9couvrez-le dans notre {privacyPolicy}."
            },
            "privacyPolicyNotice": {
                "name": "Politique d'utilisation des cookies",
                "text": "Consultez notre {privacyPolicy} pour en savoir plus."
            }
        },
        "consentNotice": {
          "changeDescription": "Des modifications ont eu lieu depuis votre derni\u00e8re visite, merci de mettre \u00e0 jour votre consentement.",
          "description": "Nous collectons et traitons vos informations personnelles dans le but suivant: les cookies statistiques permettent de suivre l'utilisation du site de manière anonyme. Ces données sont traitées uniquement pour comprendre comment les visiteurs interagissent avec le site Web.",
          "learnMore": "Param\u00e9trer les cookies"
        },
        "purposes": {
        "statistic":
          "Les cookies statistiques permettent de suivre l'utilisation du site de manière anonyme. Ces données sont traitées uniquement pour comprendre comment les visiteurs interagissent avec le site Web",
        },
        save: 'Enregistrer mon choix',
        decline: 'Refuser les cookies optionnels',
        accept: 'Accepter tous les cookies',
        acceptAll: 'Tout accepter',
        declineAll: 'Tout refuser',
        app: {
            purpose: 'Finalité'
        },    
      },
      'en-GB': {
        "consentModal": {
            "title": "We use cookies",
            "description": "What cookies do we use and why?",
            "privacyPolicy": {
                "name": "Cookie Usage Policy",
                "text": "Read about it in our {privacyPolicy}."
            },
            "privacyPolicyNotice": {
                "name": "Cookie Usage Policy",
                "text": "Check out our {privacyPolicy} to learn more."
            }
        },
        "consentNotice": {
          "changeDescription": "Changes have occurred since your last visit, please update your consent.",
          "description": "We collect and process your personal information for the following purpose: statistical cookies allow us to track site usage anonymously. This data is processed solely to understand how visitors interact with the website.",
          "learnMore": "Set cookies"
        },
        "purposes": {
        "statistic":
          "Statistical cookies allow us to track the use of the site anonymously. This data is processed solely to understand how visitors interact with the website",
        },
        save: 'Save my choice',
        decline: 'Decline optional cookies',
        accept: 'Accept all cookies',
        acceptAll: 'Accept all',
        declineAll: 'Decline all',
        app: {
            purpose: 'Purpose'
        },    
      },
      'nl-BE': {
        "consentModal": {
            "title": "Wij gebruiken cookies",
            "description": "Welke cookies gebruiken we en waarom?",
            "privacyPolicy": {
                "name": "Cookiegebruiksbeleid",
                "text": "Lees hierover in ons {privacyPolicy}."
            },
            "privacyPolicyNotice": {
                "name": "Cookiegebruiksbeleid",
                "text": "Bekijk ons {privacyPolicy} voor meer informatie."
            }
        },
        "consentNotice": {
          "changeDescription": "Er zijn veranderingen opgetreden sinds uw laatste bezoek, gelieve uw toestemming bij te werken.",
          "description": "Wij verzamelen en verwerken uw persoonsgegevens voor de volgende doeleinden: dankzij statistische cookies kunnen we het gebruik van de site anoniem bijhouden. Deze gegevens worden uitsluitend verwerkt om inzicht te krijgen in de manier waarop bezoekers met de website omgaan.",
          "learnMore": "Cookies instellen"
        },
        "purposes": {
        "statistic":
          "Dankzij statistische cookies kunnen we het gebruik van de site anoniem volgen. Deze gegevens worden uitsluitend verwerkt om inzicht te krijgen in de manier waarop bezoekers met de website omgaan.",
        },
        save: "Keuze bewaren",
        decline: "Optionele cookies weigeren",
        accept: "Alle cookies aanvaarden",
        acceptAll: "Alles aanvaarden",
        declineAll: "Alles weigeren",
        app: {
            purpose: "Doel"
        },    
      },
      'de-BE': {
        "consentModal": {
            "title": "Wir verwenden Cookies",
            "description": "Welche Cookies verwenden wir und warum?",
            "privacyPolicy": {
                "name": "Cookie-Nutzungsrichtlinie",
                "text": "Lesen Sie darüber in unserer {privacyPolicy}."
            },
            "privacyPolicyNotice": {
                "Name": "Cookie-Nutzungsrichtlinie",
                "text": "Lesen Sie unsere {privacyPolicy}, um mehr zu erfahren."
            }
        },
        "consentNotice": {
          "changeDescription": "Seit Ihrem letzten Besuch haben sich Änderungen ergeben, bitte aktualisieren Sie Ihre Zustimmung.",
          "description": "Wir sammeln und verarbeiten Ihre personenbezogenen Daten zu folgenden Zwecken: -um mit Hilfe von Statistik-Cookies anonyme Informationen über die Nutzung unserer Website zu sammeln; - um zu verstehen, wie Besucher mit der Website interagieren.",
          "learnMore": "Cookies verwalten"
        },
        "purposes": {
        "statistic":
          "Statistische Cookies ermöglichen es uns, die Nutzung der Website anonym zu verfolgen. Diese Daten werden ausschließlich verarbeitet, um zu verstehen, wie Besucher mit der Website interagieren.",
        },
        save: "Meine Wahl speichern",
        decline: "Optionale Cookies ablehnen",
        accept: "Alle Cookies akzeptieren",
        acceptAll: "Alle akzeptieren",
        declineAll: "Alle ablehnen",
        app: {
            purpose: "Zweck"
        },    
      }
    },
    apps: [
      {
        name: "google-analytics",
        title: "Google Analytics",
        purposes: ["statistic"],
        cookies: ["_ga", "_gat", "_gid", "__utma", "__utmb", "__utmc", "__utmt", "__utmz"],
        required: false,
        optOut: false
      },
    ],
  };

var translatedOpenModalElement = "Adapter\u0020les\u0020param\u00E8tres\u0020relatifs\u0020aux\u0020cookies";
var openModalElement = window.document.getElementById('openOrejimeModal');
if (openModalElement) {
    openModalElement.innerText = translatedOpenModalElement;
    openModalElement.addEventListener('click', function() {
        window.orejime.show();
    })
}
