export default {
  title: 'libfrankapy',
  description: 'Python interface for Franka Emika robots',
  base: '/libfrankapy/',
  
  ignoreDeadLinks: true,
  
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Installation', link: '/installation' },
      { text: 'Quick Start', link: '/quickstart' },
      { text: 'Examples', link: '/examples' },
      { text: 'API Reference', link: '/api/' },
      { text: 'Development', link: '/development/' }
    ],
    
    sidebar: {
      '/api/': [
        {
          text: 'API Reference',
          items: [
            { text: 'Overview', link: '/api/' },
            { text: 'Robot', link: '/api/robot' },
            { text: 'Control', link: '/api/control' },
            { text: 'State', link: '/api/state' },
            { text: 'Exceptions', link: '/api/exceptions' },
            { text: 'Utilities', link: '/api/utils' }
          ]
        }
      ],
      
      '/development/': [
        {
          text: 'Development Guide',
          items: [
            { text: 'Architecture', link: '/development/architecture' },
            { text: 'Contributing', link: '/development/contributing' },
            { text: 'Testing', link: '/development/testing' }
          ]
        }
      ]
    },
    
    socialLinks: [
      { icon: 'github', link: 'https://github.com/han-xudong/libfrankapy' }
    ],
    
    footer: {
      message: 'Released under the Apache License 2.0.',
      copyright: 'Copyright © 2025 Design & Learning Research Group'
    },
    
    search: {
      provider: 'local'
    },
    
    editLink: {
      pattern: 'https://github.com/han-xudong/libfrankapy/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    }
  }
}
