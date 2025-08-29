// 等待所有图片加载完成后设置样式
function setIngredientStyles() {
  const ingredients = document.querySelectorAll(".ingredient");
  console.log("ingredients", ingredients);

  // 检查所有图片是否都已加载
  const imagePromises = Array.from(ingredients).map((img) => {
    return new Promise((resolve) => {
      if (img.complete) {
        resolve(img);
      } else {
        img.onload = () => resolve(img);
        img.onerror = () => resolve(img); // 即使加载失败也继续
      }
    });
  });

  // 等待所有图片加载完成
  Promise.all(imagePromises).then(() => {
    let totalTopValue = 0;
    const ingredientsLen = ingredients.length;

    ingredients.forEach((img, index) => {
      const ingredientType = img.getAttribute("data-ingredient");
      const ingredientIndex = parseInt(img.getAttribute("data-index"));
      img.style.zIndex = ingredientsLen - ingredientIndex;

      // 获取当前图片高度
      const imgHeight = img.offsetHeight || img.naturalHeight || 60; // 备用默认高度
      let offsetY = 10;

      // 基础定位：从下往上堆叠
      if (ingredientType === "TopBun") {
        img.style.top = 0;
        totalTopValue = imgHeight;
      } else {
        //判断上一个食材是什么
        const prevIngredient = ingredients[index - 1];
        const prevIngredientType =
          prevIngredient.getAttribute("data-ingredient");
        //获取上一个食材的高度
        const prevIngredientHeight =
          prevIngredient.offsetHeight || prevIngredient.naturalHeight || 60;

        //上一个食材是否是辅料
        const isAuxiliary = ["cheese", "lettuce", "sauce"].includes(
          prevIngredientType
        );

        if (isAuxiliary) {
          //百分比
          const percentage = prevIngredientType === "cheese" ? 0.95 : 0.7;
          img.style.top =
            totalTopValue - prevIngredientHeight * percentage + "px";
          totalTopValue =
            totalTopValue - prevIngredientHeight * percentage + imgHeight;
        } else {
          img.style.top = totalTopValue - offsetY + "px";
          totalTopValue += imgHeight - offsetY;
        }
      }

      console.log(
        "ingredientType",
        ingredientType,
        "totalTopValue",
        totalTopValue,
        "offsetY",
        offsetY,
        "imgHeight",
        imgHeight
      );
    });

    // 滑动条逻辑处理
    setupBurgerSlider(totalTopValue);
  });
}

// 滑动条设置和控制函数
function setupBurgerSlider(burgerTotalHeight) {
  const view = document.querySelector(".view");
  const burger = document.querySelector(".burger");
  const sliderContainer = document.getElementById("sliderContainer");
  const slider = document.getElementById("burgerSlider");

  if (!view || !burger || !sliderContainer || !slider) {
    console.error("找不到必要的DOM元素");
    return;
  }

  // 获取view的可视高度
  const viewHeight = view.offsetHeight;

  console.log("汉堡总高度:", burgerTotalHeight, "可视区域高度:", viewHeight);

  // 判断是否需要显示滑动条
  if (burgerTotalHeight > viewHeight) {
    // 显示滑动条
    sliderContainer.style.display = "flex";

    // 计算可滑动的最大值
    const maxScrollValue = burgerTotalHeight - viewHeight;

    // 设置滑动条的最大值
    slider.max = maxScrollValue;
    slider.value = 0; // 初始值为0，滑动条在顶部（未选中状态）

    // 初始化burger位置（显示汉堡底部）
    burger.style.bottom = maxScrollValue + "px";

    // 滑动条事件监听
    slider.addEventListener("input", function () {
      const scrollValue = parseFloat(this.value);
      // 滑动条向下拖动时汉堡向下移动
      const bottomValue = maxScrollValue - scrollValue;
      burger.style.bottom = bottomValue + "px";
      console.log("滑动值:", scrollValue, "实际bottom值:", bottomValue);
    });

    console.log("滑动条已激活，最大滑动值:", maxScrollValue);
  } else {
    // 隐藏滑动条
    sliderContainer.style.display = "none";
    burger.style.bottom = "0px";
    console.log("汉堡高度适合，无需滑动条");
  }
}

// 响应式处理 - 窗口大小改变时重新计算
function handleResize() {
  console.log("窗口大小改变，重新计算滑动条状态");
  // 重新执行样式设置
  setIngredientStyles();
}

// 防抖函数
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 页面加载完成后执行样式设置
document.addEventListener("DOMContentLoaded", setIngredientStyles);

// 可选：添加点击事件显示食材信息
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".ingredient").forEach((img) => {
    img.addEventListener("click", function () {
      const ingredient = this.getAttribute("data-ingredient");
      const index = this.getAttribute("data-index");
      console.log(`点击了第${parseInt(index) + 1}层: ${ingredient}`);
    });
  });
});

// 窗口大小改变时重新计算（使用防抖）
window.addEventListener("resize", debounce(handleResize, 300));
