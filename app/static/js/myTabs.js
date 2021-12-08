//DOM 
//tabs grabs all objects that contain "data-tab-target"
//tabContents grabs all objects that contain "data-tab-content"
const tabs = document.querySelectorAll('[data-tab-target]')
const tabContents = document.querySelectorAll('[data-tab-content]')

tabs.forEach(tab => {
  tab.addEventListener('click', () => { //everytime we click on the tab
	//tab.dataset.tabTarget gets the tab element
	//example: <li data-tab-target="#home">Home</li>
	//tab.dataset.tabTarget gets the data-tab-target (https://developer.mozilla.org/en-US/docs/Learn/HTML/Howto/Use_data_attributes)
    const target = document.querySelector(tab.dataset.tabTarget)
	
	//removes all the tabContents
	tabContents.forEach(tabContent => {
      tabContent.classList.remove('active')
	})
	//makes the targeted tabContent active
	target.classList.add('active')

	//removes all the tabs
    tabs.forEach(tab => {
      tab.classList.remove('active')
	})
	//makes the targted tab active
    tab.classList.add('active')
  })
})